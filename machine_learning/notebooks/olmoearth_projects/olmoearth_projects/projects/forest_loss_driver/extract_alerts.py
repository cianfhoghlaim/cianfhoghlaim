"""Create prediction GeoJSON for forest loss driver classification from GLAD alerts."""

import math
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import fiona
import numpy as np
import numpy.typing as npt
import rasterio
import rasterio.features
import shapely
import shapely.affinity
import shapely.geometry
import shapely.ops
import tqdm
from rasterio.crs import CRS
from rslearn.const import SHAPEFILE_AUX_EXTENSIONS, WGS84_PROJECTION
from rslearn.utils.feature import Feature
from rslearn.utils.fsspec import get_upath_local, open_rasterio_upath_reader
from rslearn.utils.geometry import PixelBounds, Projection, STGeometry
from rslearn.utils.raster_format import get_raster_projection_and_bounds
from rslearn.utils.vector_format import GeojsonCoordinateMode, GeojsonVectorFormat
from upath import UPath

from olmoearth_projects.utils.logging import get_logger

logger = get_logger(__name__)

# Time corresponding to 0 in alertDate GeoTIFF files.
BASE_DATETIME = datetime(2019, 1, 1, tzinfo=UTC)

# Create windows at WebMercator zoom 13 (512x512 tiles).
WEB_MERCATOR_CRS = CRS.from_epsg(3857)
WEB_MERCATOR_M = 2 * math.pi * 6378137
PIXEL_SIZE = WEB_MERCATOR_M / (2**13) / 512
WEB_MERCATOR_PROJECTION = Projection(WEB_MERCATOR_CRS, PIXEL_SIZE, -PIXEL_SIZE)

ANNOTATION_WEBSITE_MERCATOR_OFFSET = 512 * (2**12)


@dataclass
class ExtractAlertsArgs:
    """Arguments for extract_alerts_pipeline.

    Args:
        gcs_tiff_filenames: the list of GCS TIFF filenames to extract alerts from.
        out_fname: the filename to write the prediction request geometry.
        country_data_path: the path to the country shapefile. It should be downloaded
            and extracted from https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/
        countries: limit alerts to those falling in these countries. It is a list of
            two-letter uppercase country codes, e.g. ["PE"] for Peru only.
        conf_prefix: the prefix for the confidence raster of the forest loss alerts.
        date_prefix: the prefix for the date raster of the forest loss alerts.
        prediction_utc_time: the UTC time of the prediction. This defaults to the
            current timestamp, but could be set to the past to look for historical
            forest loss drivers.
        min_confidence: the minimum confidence threshold.
        days: the number of days to consider before the prediction time.
        min_area: the minimum area threshold for an event to be extracted.
        max_number_of_events: the maximum number of events to extract per GLAD tile.
        workers: the number of worker processes to use.
    """

    gcs_tiff_filenames: list[str]
    out_fname: str

    country_data_path: str = "./ne_10m_admin_0_countries.shp"
    countries: list[str] | None = None

    conf_prefix: str = "gs://earthenginepartners-hansen/S2alert/alert/"
    date_prefix: str = "gs://earthenginepartners-hansen/S2alert/alertDate/"
    prediction_utc_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    min_confidence: int = 2
    days: int = 365
    min_area: float = 16.0
    max_number_of_events: int | None = None
    workers: int = 32


def load_country_polygon(
    country_data_path: UPath, countries: list[str]
) -> shapely.Geometry:
    """Get the polygons corresponding to the specified countries.

    country_data_path should point to the shapefile downloaded and extracted from
    https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/,
    and the parent directory must contain the other auxiliary files too.
    """
    logger.info(f"loading country polygon from {country_data_path}")
    prefix = ".".join(country_data_path.name.split(".")[:-1])
    aux_files: list[UPath] = []
    for ext in SHAPEFILE_AUX_EXTENSIONS:
        aux_files.append(country_data_path.parent / (prefix + ext))
    country_wgs84_shp: shapely.Geometry | None = None
    with get_upath_local(country_data_path, extra_paths=aux_files) as local_fname:
        with fiona.open(local_fname) as src:
            for feat in src:
                if feat["properties"]["ISO_A2"] not in countries:
                    continue
                cur_shp = shapely.geometry.shape(feat["geometry"])
                if country_wgs84_shp:
                    country_wgs84_shp = country_wgs84_shp.union(cur_shp)
                else:
                    country_wgs84_shp = cur_shp

    assert country_wgs84_shp is not None
    return country_wgs84_shp


def process_shapes_into_events(
    tif_fname: str,
    shapes: list[shapely.Geometry],
    date_data: npt.NDArray,
    projection: Projection,
    bounds: PixelBounds,
    country_wgs84_shp: shapely.Polygon,
    min_area: float,
) -> list[Feature]:
    """Process the forest loss shapes into vector features.

    Args:
        tif_fname: the GLAD tile filename.
        shapes: the shapes extracted from the forest loss mask.
        date_data: the GLAD date raster.
        projection: the projection of the pixel coordinates.
        bounds: the bounds of the pixel coordinates.
        country_wgs84_shp: the country polygon to limit events to.
        min_area: minimum area constraint for each shape.
    """
    events: list[Feature] = []
    background_skip_count = 0
    area_skip_count = 0
    country_skip_count = 0

    for shp, value in tqdm.tqdm(shapes, desc="process shapes"):
        # Skip shapes corresponding to the background.
        if value != 1:
            background_skip_count += 1
            continue

        # Apply minimum area constraint, it must be in GLAD pixels which should be
        # 10 m/pixel.
        shp = shapely.geometry.shape(shp)
        if shp.area < min_area:
            area_skip_count += 1
            continue

        # Get center point (clipped to shape) and note the corresponding date.
        center_shp, _ = shapely.ops.nearest_points(shp, shp.centroid)
        center_pixel = (int(center_shp.x), int(center_shp.y))
        cur_days = int(date_data[center_pixel[1], center_pixel[0]])

        if cur_days == 0:
            # Sometimes this can happen if the clipping was off a bit, and the
            # center_pixel is outside the connected component of alert pixels.
            continue

        cur_date = BASE_DATETIME + timedelta(days=cur_days)

        # Verify that the center is in the country polygon.
        center_src_geom = STGeometry(
            projection,
            shapely.Point(center_pixel[0] + bounds[0], center_pixel[1] + bounds[1]),
            (cur_date, cur_date),
        )
        center_wgs84_geom = center_src_geom.to_projection(WGS84_PROJECTION)
        if country_wgs84_shp is not None and not country_wgs84_shp.contains(
            center_wgs84_geom.shp
        ):
            country_skip_count += 1
            continue

        polygon_src_geom = STGeometry(
            projection,
            shapely.affinity.translate(shp, xoff=bounds[0], yoff=bounds[1]),
            (cur_date, cur_date),
        )
        polygon_wgs84_geom = polygon_src_geom.to_projection(WGS84_PROJECTION)
        events.append(
            Feature(
                polygon_wgs84_geom,
                properties=dict(
                    center_pixel=center_pixel,
                    tif_fname=tif_fname,
                    oe_start_time=cur_date.isoformat(),
                    oe_end_time=cur_date.isoformat(),
                ),
            )
        )

    logger.debug(f"Skipped {background_skip_count} shapes as background")
    logger.debug(f"Skipped {area_skip_count} shapes due to area")
    logger.debug(f"Skipped {country_skip_count} shapes not in country polygon")
    return events


def extract_events_for_tile(
    args: ExtractAlertsArgs,
    tif_fname: str,
    country_wgs84_shp: shapely.Geometry | None,
) -> list[Feature]:
    """Extract vector features of forest loss events for the given GLAD alert tile.

    Args:
        args: the ExtractAlertsArgs.
        tif_fname: the GLAD alert tile filename to process.
        country_wgs84_shp: the country geometry to limit events to.

    Returns:
        list of vector features.
    """
    # Read the confidence and date rasters from GCS, where they are published.
    # We also get the projection and bounds, which we can use for corodinate
    # transforms.
    conf_path = UPath(args.conf_prefix) / tif_fname
    logger.info(f"Read confidences from {conf_path}")
    with open_rasterio_upath_reader(conf_path) as src:
        conf_data = src.read(1)
        projection, bounds = get_raster_projection_and_bounds(src)

    date_path = UPath(args.date_prefix) / tif_fname
    logger.info(f"Read dates from {conf_path}")
    with open_rasterio_upath_reader(date_path) as src:
        date_data = src.read(1)

    # Now we compute the mask based on the confidence and date conditions.
    logger.info("Compute overall mask")
    now_days = (args.prediction_utc_time - BASE_DATETIME).days
    min_days = now_days - args.days
    date_mask = date_data >= min_days
    conf_mask = conf_data >= args.min_confidence
    forest_loss_mask = (date_mask & conf_mask).astype(np.uint8)

    if np.count_nonzero(forest_loss_mask) == 0:
        logger.warning(
            f"No forest loss events found for {tif_fname}, skipping further processing for this tile"
        )
        return []

    # Extract shapely geometries from the mask.
    logger.info(f"Create shapes from mask for {tif_fname}")
    shapes = list(rasterio.features.shapes(forest_loss_mask))

    # Finally we can process those shapes into forest loss events.
    return process_shapes_into_events(
        tif_fname=tif_fname,
        shapes=shapes,
        date_data=date_data,
        projection=projection,
        bounds=bounds,
        country_wgs84_shp=country_wgs84_shp,
        min_area=args.min_area,
    )


def extract_alerts(
    extract_alerts_args: ExtractAlertsArgs,
) -> None:
    """Create a prediction request geometry based on GLAD alerts.

    Args:
        extract_alerts_args: the extract_alerts_args
    """
    logger.info(f"Extract_alerts for {str(extract_alerts_args)}")

    # Get country geometries to limit the area where we look for alerts.
    country_wgs84_shp: shapely.Geometry | None = None
    if extract_alerts_args.countries is not None:
        country_wgs84_shp = load_country_polygon(
            UPath(extract_alerts_args.country_data_path), extract_alerts_args.countries
        )

    # Process the GLAD alert tiles one tile at a time.
    # Each tile has two files we need to read, the confidence raster (which we use to
    # threshold pixels by confidence threshold) and date raster (which we use to only
    # select pixels with recent forest loss based on specified number of days).
    events: list[Feature] = []

    for fname in extract_alerts_args.gcs_tiff_filenames:
        # Get the events.
        cur_events = extract_events_for_tile(
            extract_alerts_args, fname, country_wgs84_shp=country_wgs84_shp
        )

        # Limit to maximum number of events if desired.
        if (
            extract_alerts_args.max_number_of_events is not None
            and len(cur_events) > extract_alerts_args.max_number_of_events
        ):
            logger.info(
                f"Limiting from {len(cur_events)} to {extract_alerts_args.max_number_of_events} events"
            )
            cur_events = random.sample(
                cur_events, extract_alerts_args.max_number_of_events
            )

        logger.info(f"Writing {len(cur_events)} windows")
        events.extend(cur_events)

    logger.info(f"Total events: {len(events)}")

    GeojsonVectorFormat(coordinate_mode=GeojsonCoordinateMode.WGS84).encode_to_file(
        UPath(extract_alerts_args.out_fname), events
    )
