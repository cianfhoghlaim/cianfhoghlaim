import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.util.ArrayList;

/**
   A style for a segmented line that indicates the number
   and sequence of bends.
*/
public enum BentStyle
{
   STRAIGHT, HV, VH, HVH, VHV;

   /**
      Gets the points at which a line joining two rectangles
      is bent according to this bent style.
      @param start the starting rectangle
      @param end the ending rectangle
      @return an array list of points at which to bend the
      segmented line joining the two rectangles
   */
   public ArrayList<Point2D> getPath(Rectangle2D start, Rectangle2D end)
   {
      ArrayList<Point2D> r = getPath(this, start, end);
      if (r != null) return r;

      if (this == HVH) r = getPath(VHV, start, end);
      else if (this == VHV) r = getPath(HVH, start, end);
      else if (this == HV) r = getPath(VH, start, end);
      else if (this == VH) r = getPath(HV, start, end);
      if (r != null) return r;

      return getPath(STRAIGHT, start, end);
   }

   /**
      Gets the four connecting points at which a bent line
      connects to a rectangle.
   */
   private static Point2D[] connectionPoints(Rectangle2D r)
   {
      Point2D[] a = new Point2D[4];
      a[0] = new Point2D.Double(r.getX(), r.getCenterY());
      a[1] = new Point2D.Double(r.getMaxX(), r.getCenterY());
      a[2] = new Point2D.Double(r.getCenterX(), r.getY());
      a[3] = new Point2D.Double(r.getCenterX(), r.getMaxY());
      return a;
   }

   /**
      Gets the points at which a line joining two rectangles
      is bent according to a bent style.
      @param start the starting rectangle
      @param end the ending rectangle
      @return an array list of points at which to bend the
      segmented line joining the two rectangles
   */
   private static ArrayList<Point2D> getPath(BentStyle bent,
      Rectangle2D s, Rectangle2D e)
   {
      ArrayList<Point2D> r = new ArrayList<Point2D>();
      if (bent == STRAIGHT)
      {
         Point2D[] a = connectionPoints(s);
         Point2D[] b = connectionPoints(e);
         Point2D p = a[0];
         Point2D q = b[0];
         double distance = p.distance(q);
         //for (int i = 0; i < a.length; i++)
         for (Point2D point1 : a)
            //for (int j = 0; j < b.length; j++)
            for (Point2D point2 : b)
            {
               double d = point1.distance(point2);
               if (d < distance)
               {
                  p = point1; q = point2;
                  distance = d;
               }
            }
         r.add(p);
         r.add(q);
      }
      else if (bent == HV)
      {
         double x1;
         double x2 = e.getCenterX();
         double y1 = s.getCenterY();
         double y2;
         if (x2 + MIN_SEGMENT <= s.getX())
            x1 = s.getX();
         else if (x2 - MIN_SEGMENT >= s.getMaxX())
            x1 = s.getMaxX();
         else return null;
         if (y1 + MIN_SEGMENT <= e.getY())
            y2 = e.getY();
         else if (y1 - MIN_SEGMENT >= e.getMaxY())
            y2 = e.getMaxY();
         else return null;
         r.add(new Point2D.Double(x1, y1));
         r.add(new Point2D.Double(x2, y1));
         r.add(new Point2D.Double(x2, y2));
      }
      else if (bent == VH)
      {
         double x1 = s.getCenterX();
         double x2;
         double y1;
         double y2 = e.getCenterY();
         if (x1 + MIN_SEGMENT <= e.getX())
            x2 = e.getX();
         else if (x1 - MIN_SEGMENT >= e.getMaxX())
            x2 = e.getMaxX();
         else return null;
         if (y2 + MIN_SEGMENT <= s.getY())
            y1 = s.getY();
         else if (y2 - MIN_SEGMENT >= s.getMaxY())
            y1 = s.getMaxY();
         else return null;
         r.add(new Point2D.Double(x1, y1));
         r.add(new Point2D.Double(x1, y2));
         r.add(new Point2D.Double(x2, y2));
      }
      else if (bent == HVH)
      {
         double x1;
         double x2;
         double y1 = s.getCenterY();
         double y2 = e.getCenterY();
         if (s.getMaxX() + 2 * MIN_SEGMENT <= e.getX())
         {
            x1 = s.getMaxX();
            x2 = e.getX();
         }
         else if (e.getMaxX() + 2 * MIN_SEGMENT <= s.getX())
         {
            x1 = s.getX();
            x2 = e.getMaxX();
         }
         else return null;
         if (Math.abs(y1 - y2) <= MIN_SEGMENT)
         {
            r.add(new Point2D.Double(x1, (y1 + y2) / 2));
            r.add(new Point2D.Double(x2, (y1 + y2) / 2));
         }
         else
         {
            r.add(new Point2D.Double(x1, y1));
            r.add(new Point2D.Double((x1 + x2) / 2, y1));
            r.add(new Point2D.Double((x1 + x2) / 2, y2));
            r.add(new Point2D.Double(x2, y2));
         }
      }
      else if (bent == VHV)
      {
         double x1 = s.getCenterX();
         double x2 = e.getCenterX();
         double y1;
         double y2;
         if (s.getMaxY() + 2 * MIN_SEGMENT <= e.getY())
         {
            y1 = s.getMaxY();
            y2 = e.getY();
         }
         else if (e.getMaxY() + 2 * MIN_SEGMENT <= s.getY())
         {
            y1 = s.getY();
            y2 = e.getMaxY();

         }
         else return null;
         if (Math.abs(x1 - x2) <= MIN_SEGMENT)
         {
            r.add(new Point2D.Double((x1 + x2) / 2, y1));
            r.add(new Point2D.Double((x1 + x2) / 2, y2));
         }
         else
         {
            r.add(new Point2D.Double(x1, y1));
            r.add(new Point2D.Double(x1, (y1 + y2) / 2));
            r.add(new Point2D.Double(x2, (y1 + y2) / 2));
            r.add(new Point2D.Double(x2, y2));
         }
      }
      else return null;
      return r;
   }

   private static final int MIN_SEGMENT = 10;
}
