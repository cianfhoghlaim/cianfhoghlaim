import java.awt.*;
import java.awt.geom.*;

/**
   A house shape.
*/
public class HouseShape extends CompoundShape
{
   /**
      Constructs a house shape.
      @param x the left of the bounding rectangle
      @param y the top of the bounding rectangle
      @param width the width of the bounding rectangle
   */
   public HouseShape(int x, int y, int width)
   {
      Rectangle2D.Double base 
         = new Rectangle2D.Double(x, y + width, width, width);

      // The left bottom of the roof
      Point2D.Double r1
         = new Point2D.Double(x, y + width);
      // The top of the roof
      Point2D.Double r2
         = new Point2D.Double(x + width / 2, y);
      // The right bottom of the roof
      Point2D.Double r3
         = new Point2D.Double(x + width, y + width);

      Line2D.Double roofLeft
         = new Line2D.Double(r1, r2);
      Line2D.Double roofRight
         = new Line2D.Double(r2, r3);

      add(base);
      add(roofLeft);
      add(roofRight);
   }
}
