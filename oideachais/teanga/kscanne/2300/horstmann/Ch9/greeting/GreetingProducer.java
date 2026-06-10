/**
   An action that repeatedly prints a greeting.
*/
public class GreetingProducer implements Runnable
{
   /**
      Constructs the producer object.
      @param aGreeting the greeting to display
   */
   public GreetingProducer(String aGreeting)
   {
      greeting = aGreeting;
   }

   public void run()
   {
      try 
      {
         for (int i = 1; i <= REPETITIONS; i++)
         {
            System.out.println(i + ": " + greeting);
            Thread.sleep(DELAY);                     
         }
      }
      catch (InterruptedException exception)
      {
      }
   }

   private String greeting;

   private static final int REPETITIONS = 10;
   private static final int DELAY = 100;
}
