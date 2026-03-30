/** 
    A first-in, first-out bounded collection of objects. 
*/ 
public class BoundedQueue<E>
{ 
   /** 
       Constructs an empty queue. 
       @param capacity the maximum capacity of the queue 
   */ 
   public BoundedQueue(int capacity) 
   { 
      elements = new Object[capacity]; 
      head = 0; 
      tail = 0; 
      size = 0;
   } 

   /** 
       Removes the object at the head. 
       @return the object that has been removed from the queue
   */ 
   public synchronized E remove() 
         throws InterruptedException
   { 
      while (size == 0) wait();
      E r = (E) elements[head]; 
      head++;
      size--;
      if (head == elements.length) 
         head = 0; 
      notifyAll();
      return r; 
   } 

   /** 
       Appends an object at the tail. 
       @param newValue the object to be appended 
   */ 
   public synchronized void add(E newValue) 
         throws InterruptedException
   { 
      while (size == elements.length) wait();
      elements[tail] = newValue; 
      tail++;
      size++;
      if (tail == elements.length) 
         tail = 0; 
      notifyAll();
   } 

   private Object[] elements; 
   private int head; 
   private int tail; 
   private int size;
}
