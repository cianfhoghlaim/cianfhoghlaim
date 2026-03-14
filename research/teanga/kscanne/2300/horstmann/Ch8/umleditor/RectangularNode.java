import java.awt.Graphics2D;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.awt.geom.RectangularShape;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

/**
   A node that has a rectangular shape.
*/
public abstract class RectangularNode implements Node
{
   public Object clone()
   {
      try
      {
         RectangularNode cloned = (RectangularNode) super.clone();
         cloned.bounds = (Rectangle2D) bounds.clone();
         return cloned;      
      }
      catch (CloneNotSupportedException exception)
      {
         return null;
      }    
   }

   public void translate(double dx, double dy)
   {
      bounds.setFrame(bounds.getX() + dx,
         bounds.getY() + dy, 
         bounds.getWidth(), 
         bounds.getHeight());
   }

   public boolean contains(Point2D p)
   {
      return bounds.contains(p);
   }

   public Rectangle2D getBounds()
   {
      return (Rectangle2D) bounds.clone();
   }

   public void setBounds(Rectangle2D newBounds)
   {
      bounds = newBounds;
   }

   public Point2D getConnectionPoint(Point2D aPoint)
   {
      double slope = bounds.getHeight() / bounds.getWidth();
      double x = bounds.getCenterX();
      double y = bounds.getCenterY();
      double ex = aPoint.getX() - x;
      double ey = aPoint.getY() - y;
      
      if (ex != 0 && -slope <= ey / ex && ey / ex <= slope)
      {  
         // intersects at left or right boundary
         if (ex > 0) 
         {
            x = bounds.getMaxX();
            y += (bounds.getWidth() / 2) * ey / ex;
         }
         else
         {
            x = bounds.getX();
            y -= (bounds.getWidth() / 2) * ey / ex;
         }
      }
      else if (ey != 0)
      {  
         // intersects at top or bottom
         if (ey > 0) 
         {
            x += (bounds.getHeight() / 2) * ex / ey;
            y = bounds.getMaxY();
         }
         else
         {
            x -= (bounds.getHeight() / 2) * ex / ey;
            y = bounds.getY();
         }
      }
      return new Point2D.Double(x, y);
   }

   private void writeObject(ObjectOutputStream out)
      throws IOException
   {
      out.defaultWriteObject();
      writeRectangularShape(out, bounds);
   }

   /**
      A helper method to overcome the problem that the 2D shapes
      aren't serializable. It writes x, y, width and height
      to the stream.
      @param out the stream
      @param s the shape      
   */
   private static void writeRectangularShape(
      ObjectOutputStream out, 
      RectangularShape s)
      throws IOException
   {
      out.writeDouble(s.getX());
      out.writeDouble(s.getY());
      out.writeDouble(s.getWidth());
      out.writeDouble(s.getHeight());
   }

   private void readObject(ObjectInputStream in)
      throws IOException, ClassNotFoundException
   {
      in.defaultReadObject();
      bounds = new Rectangle2D.Double();
      readRectangularShape(in, bounds);
   }
   
   /**
      A helper method to overcome the problem that the 2D shapes
      aren't serializable. It reads x, y, width and height
      from the stream.
      @param in the stream
      @param s the shape whose frame is set from the stream values
   */
   private static void readRectangularShape(ObjectInputStream in,
      RectangularShape s)
      throws IOException
   {
      double x = in.readDouble();
      double y = in.readDouble();
      double width = in.readDouble();
      double height = in.readDouble();
      s.setFrame(x, y, width, height);
   }

   private transient Rectangle2D bounds;
}
