"""
dlt pipeline for Leaving Certificate syllabus and exam extraction.
Extracts PDFs from examinations.ie and curriculumonline.ie,
and stores them in Garage S3 and metadata in MotherDuck.
"""

import os
from typing import Iterator, Dict, Any, List

import dlt
from dlt.sources.helpers import requests

@dlt.source
def leaving_cert_source(years: List[int], subjects: List[str]) -> Iterator[dlt.resource]:
    """
    Source for Leaving Certificate exams and syllabus.
    """
    yield exam_papers(years, subjects)
    yield marking_schemes(years, subjects)
    yield syllabus_documents(subjects)


def download_and_upload_to_s3(url: str, s3_key: str) -> str:
    """
    Mock function: Downloads a PDF from a URL and uploads it to Garage S3.
    Returns the S3 URI.
    """
    # In a real scenario, we use requests to get the PDF binary
    # and boto3 to upload to Garage S3.
    # response = requests.get(url)
    # s3_client.put_object(Bucket="education-documents", Key=s3_key, Body=response.content)
    
    bucket = os.environ.get("GARAGE_BUCKET", "education-documents")
    return f"s3://{bucket}/{s3_key}"


@dlt.resource(name="exam_papers", write_disposition="merge", primary_key=["subject", "year", "level"])
def exam_papers(years: List[int], subjects: List[str]) -> Iterator[Dict[str, Any]]:
    """Resource yielding metadata for exam papers."""
    for year in years:
        for subject in subjects:
            for level in ["Higher", "Ordinary"]:
                # Mock URL generation
                url = f"https://www.examinations.ie/archive/exampapers/{year}/LC_{subject}_{level}.pdf"
                s3_key = f"exams/{year}/LC_{subject}_{level}.pdf"
                
                s3_uri = download_and_upload_to_s3(url, s3_key)
                
                yield {
                    "subject": subject,
                    "year": year,
                    "level": level,
                    "document_type": "exam_paper",
                    "source_url": url,
                    "s3_uri": s3_uri,
                    "language": "ga" if subject == "gaeilge" else "en"
                }


@dlt.resource(name="marking_schemes", write_disposition="merge", primary_key=["subject", "year", "level"])
def marking_schemes(years: List[int], subjects: List[str]) -> Iterator[Dict[str, Any]]:
    """Resource yielding metadata for marking schemes."""
    for year in years:
        for subject in subjects:
            for level in ["Higher", "Ordinary"]:
                url = f"https://www.examinations.ie/archive/markingschemes/{year}/LC_{subject}_{level}_MS.pdf"
                s3_key = f"marking_schemes/{year}/LC_{subject}_{level}_MS.pdf"
                
                s3_uri = download_and_upload_to_s3(url, s3_key)
                
                yield {
                    "subject": subject,
                    "year": year,
                    "level": level,
                    "document_type": "marking_scheme",
                    "source_url": url,
                    "s3_uri": s3_uri,
                    "language": "ga" if subject == "gaeilge" else "en"
                }


@dlt.resource(name="syllabus_documents", write_disposition="merge", primary_key=["subject"])
def syllabus_documents(subjects: List[str]) -> Iterator[Dict[str, Any]]:
    """Resource yielding metadata for syllabus specifications."""
    for subject in subjects:
        url = f"https://www.curriculumonline.ie/getmedia/lc_{subject}_syllabus.pdf"
        s3_key = f"syllabus/LC_{subject}.pdf"
        
        s3_uri = download_and_upload_to_s3(url, s3_key)
        
        yield {
            "subject": subject,
            "document_type": "syllabus",
            "source_url": url,
            "s3_uri": s3_uri,
            "language": "ga" if subject == "gaeilge" else "en"
        }
