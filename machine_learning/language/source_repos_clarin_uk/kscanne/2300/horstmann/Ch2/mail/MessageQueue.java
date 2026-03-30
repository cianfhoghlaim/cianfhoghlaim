import java.util.ArrayList;

/**
   A first-in, first-out collection of messages. This
   implementation is not very efficient. We will consider
   a more efficient implementation in chapter 3.
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
      return queue.remove(0);
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
   public int size()
   {
      return queue.size();
   }

   /**
      Get message at head.
      @return message that is at the head of the queue, or null
      if the queue is empty
   */
   public Message peek()
   {
      if (queue.size() == 0) return null;
      else return queue.get(0);
   }

   private ArrayList<Message> queue;
}
