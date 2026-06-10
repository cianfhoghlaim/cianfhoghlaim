import java.awt.*;
import java.awt.geom.*;
import java.io.*;

/**
   A serializable car shape.
*/
public class Car implements Serializable
{
   /**
      Constructs a car.
      @param x the left of the bounding rectangle
      @param y the top of the bounding rectangle
      @param width the width of the bounding rectangle
   */
   public Car(int x, int y, int width)
   {
      body = new Rectangle(x, y + width / 6,
         width - 1, width / 6);
      roof = new Rectangle(x + width / 3, y,
         width / 3, width / 6);
      frontTire = new Ellipse2D.Double(x + width / 6, y + width / 3,
         width / 6, width / 6);
      rearTire = new Ellipse2D.Double(x + width * 2 / 3, y + width / 3,
         width / 6, width / 6);
   }

   private void writeObject(ObjectOutputStream out)
      throws IOException
   {
      out.defaultWriteObject();
      writeRectangularShape(out, frontTire);
      writeRectangularShape(out, rearTire);
   }

   /**
      A helper method to write a rectangular shape.
      @param out the stream onto which to write the shape
      @param s the shape to write
   */
   private static void writeRectangularShape(ObjectOutputStream out,
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
      frontTire = new Ellipse2D.Double();
      readRectangularShape(in, frontTire);
      rearTire = new Ellipse2D.Double();
      readRectangularShape(in, rearTire);
   }

   /**
      A helper method to read a rectangular shape.
      @param in the stream from which to read the shape
      @param s the shape to read. The method sets the frame
      of this rectangular shape.
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

   /**
      Draws the car.
      @param g2 the graphics context
   */
   public void draw(Graphics2D g2)
   {
      g2.draw(body);
      g2.draw(roof);
      g2.draw(frontTire);
      g2.draw(rearTire);
   }

   public String toString()
   {
      return getClass().getName()
         + "[body=" + body
         + ",roof=" + roof
         + ",frontTire=" + formatRectangularShape(frontTire)
         + ",rearTire=" + formatRectangularShape(rearTire)
         + "]";
   }

   /**
      A helper method to format a rectangular shape.
      @param s the shape to format
      @return a formatted representation of the given shape
   */
   private static String formatRectangularShape(RectangularShape s)
   {
      return RectangularShape.class.getName()
         + "[x=" + s.getX()
         + ",y=" + s.getY()
         + ",width=" + s.getWidth()
         + ",height=" + s.getHeight()
         + "]";
   }


   private Rectangle body;
   private Rectangle roof;
   private transient Ellipse2D.Double frontTire;
   private transient Ellipse2D.Double rearTire;
}


