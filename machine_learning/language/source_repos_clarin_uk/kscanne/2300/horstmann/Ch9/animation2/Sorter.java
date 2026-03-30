import java.util.*;
import java.util.concurrent.*;

/**
   This runnable executes a sort algorithm.
   When two elements are compared, the algorithm
   pauses and updates a panel.
*/
public class Sorter implements Runnable
{
   public Sorter(Double[] values, ArrayComponent panel, BlockingQueue<String> queue)
   {
      this.values = values;
      this.panel = panel;
      this.queue = queue;
   }

   public void run()
   {
      Comparator<Double> comp = new
         Comparator<Double>()
         {
            public int compare(Double d1, Double d2)
            {
               try
               {
                  String command = queue.take();
                  if (command.equals("Run"))
                  {
                     Thread.sleep(DELAY);
                     if (!"Step".equals(queue.peek()))
                        queue.add("Run");
                  }
               }
               catch (InterruptedException exception)
               {
                  Thread.currentThread().interrupt();
               }
               panel.setValues(values, d1, d2);
               return d1.compareTo(d2);
            }
         };
      MergeSorter.sort(values, comp);
      panel.setValues(values, null, null);
   }

   private Double[] values;
   private ArrayComponent panel;
   private BlockingQueue<String> queue;
   private static final int DELAY = 100;
}
