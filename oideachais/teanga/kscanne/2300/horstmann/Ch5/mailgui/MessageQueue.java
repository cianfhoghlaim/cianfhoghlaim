import java.util.ArrayList;

/**
   A first-in, first-out bounded collection of messages.
*/
public class MessageQueue
{
   /**
      Constructs an empty message queue.
   */
   public MessageQueue()
   {
      queue = new ArrayList<Message>();
   }

   /**
      Remove message at head.
      @return message that has been removed from the queue
   */
   public Message remove()
   {
      if (!queue.isEmpty())
         return queue.remove(0);
      else
         throw new IllegalStateException("Queue is empty");
   }

   /**
      Append message at tail.
      @param newMessage the message to be appended
   */
   public void add(Message newMessage)
   {
      queue.add(newMessage);
   }

   /**
      Get the total number of messages in the queue.
      @return the total number of messages in the queue
   */
   public int getLength()
   {
      return queue.size();
   }

   /**
      Get message at head.
      @return message that is at the head of the queue
   */
   public Message getHead()
   {
      if (!queue.isEmpty())
         return queue.get(0);
      else
         throw new IllegalStateException("Queue is empty");
   }

   private ArrayList<Message> queue;
}
