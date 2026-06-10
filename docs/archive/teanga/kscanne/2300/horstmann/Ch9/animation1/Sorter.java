import java.util.*;

/**
   This runnable executes a sort algorithm.
   When two elements are compared, the algorithm
   pauses and updates a panel.
*/
public class Sorter implements Runnable
{
   /**
      Constructs the sorter.
      @param values the array to sort
      @param panel the panel for displaying the array
   */
   public Sorter(Double[] values, ArrayComponent panel)
   {
      this.values = values;
      this.panel = panel;
   }

   public void run()
   {
      Comparator<Double> comp = new
         Comparator<Double>()
         {
            public int compare(Double d1, Double d2)
            {
               panel.setValues(values, d1, d2);
               try
               {
                  Thread.sleep(DELAY);
               }
               catch (InterruptedException exception)
               {
                  Thread.currentThread().interrupt();
               }
               return (d1).compareTo(d2);
            }
         };
      MergeSorter.sort(values, comp);
      panel.setValues(values, null, null);
   }

   private Double[] values;
   private ArrayComponent panel;
   private static final int DELAY = 100;
}
