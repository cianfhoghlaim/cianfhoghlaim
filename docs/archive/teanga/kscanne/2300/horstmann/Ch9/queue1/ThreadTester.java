/**
   This program runs two threads in parallel.
*/
public class ThreadTester
{
   public static void main(String[] args)
   {
      BoundedQueue<String> queue = new BoundedQueue<String>(10);
      queue.setDebug(true);
      final int GREETING_COUNT = 100;
      Runnable run1 = new Producer("Hello, World!", 
            queue, GREETING_COUNT);
      Runnable run2 = new Producer("Goodbye, World!", 
            queue, GREETING_COUNT);
      Runnable run3 = new Consumer(queue, 2 * GREETING_COUNT);
      
      Thread thread1 = new Thread(run1);
      Thread thread2 = new Thread(run2);
      Thread thread3 = new Thread(run3);

      thread1.start();
      thread2.start();
      thread3.start();
   }
}

