import java.util.*;

public class Utils
{
   public static <E> void fill(ArrayList<E> a, E value, int count)
   {
      for (int i = 0; i < count; i++)
         a.add(value);
   }

   public static <E, F extends E> void append(ArrayList<E> a, 
         ArrayList<F> b, int count)
   {
      for (int i = 0; i < count && i < b.size(); i++)
         a.add(b.get(i));
   }

   public static <E extends Comparable<? super E>> 
         E getMax(ArrayList<E> a)
   {
      E max = a.get(0);
      for (int i = 1; i < a.size(); i++)
         if (a.get(i).compareTo(max) > 0) max = a.get(i);
      return max;
   }

   public static <E> void fillWithDefaults(ArrayList<E> a, 
         Class<? extends E> cl, int count) 
         throws InstantiationException, IllegalAccessException
   {
      for (int i = 0; i < count; i++)
         a.add(cl.newInstance());
   }
}
