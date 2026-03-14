import java.lang.reflect.*;
import java.util.*;

/**
   This program shows how to use reflection to print
   the names and values of all nonstatic fields of an object.
*/
public class FieldTester
{
   public static void main(String[] args)
         throws IllegalAccessException
   {
      Random r = new Random();
      System.out.print(spyFields(r));
      r.nextInt();
      System.out.println("\nAfter calling nextInt:\n");      
      System.out.print(spyFields(r));
   }

   /**
      Spies on the field names and values of an object.
      @param obj the object whose fields to format
      @return a string containing the names and values of
      all fields of obj
   */
   public static String spyFields(Object obj)
         throws IllegalAccessException
   {
      StringBuffer buffer = new StringBuffer();
      Field[] fields = obj.getClass().getDeclaredFields();
      for (Field f : fields)
      {
         if (!Modifier.isStatic(f.getModifiers()))
         {
            f.setAccessible(true);
            Object value = f.get(obj);
            buffer.append(f.getType().getName());
            buffer.append(" ");
            buffer.append(f.getName());
            buffer.append("=");
            buffer.append("" + value);
            buffer.append("\n");
         }
      }
      return buffer.toString();
   }
}
