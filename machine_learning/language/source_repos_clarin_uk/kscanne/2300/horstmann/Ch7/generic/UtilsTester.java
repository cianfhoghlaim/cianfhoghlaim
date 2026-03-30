import java.util.*;
import java.awt.*;

public class UtilsTester
{
   public static void main(String[] args)
         throws InstantiationException, IllegalAccessException
   {
      ArrayList<String> ids = new ArrayList<String>(); 
      Utils.fill(ids, "default", 10);
      System.out.println(ids);

      ArrayList<Shape> shapes = new ArrayList<Shape>();
      Utils.fill(shapes, new Rectangle(5, 10, 20, 30), 2);
      System.out.println(shapes);

      ArrayList<Polygon> polys = new ArrayList<Polygon>();
      Utils.fillWithDefaults(polys, Polygon.class, 10);
      Utils.append(shapes, polys, 2);
      System.out.println(shapes);      

      ArrayList<GregorianCalendar> dates 
            = new ArrayList<GregorianCalendar>();
      Utils.fillWithDefaults(dates, GregorianCalendar.class, 5);
      System.out.println(Utils.getMax(dates));
   }
}
