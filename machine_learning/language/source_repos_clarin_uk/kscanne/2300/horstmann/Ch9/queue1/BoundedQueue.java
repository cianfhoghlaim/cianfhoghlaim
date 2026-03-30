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
       @precondition !isEmpty()
   */ 
   public E remove() 
   { 
      if (debug) System.out.print("removeFirst");
      E r = (E) elements[head]; 
      if (debug) System.out.print(".");
      head++;
      if (debug) System.out.print(".");
      size--;
      if (head == elements.length) 
      {
         if (debug) System.out.print(".");
         head = 0; 
      }
      if (debug) 
         System.out.println("head=" + head + ",tail=" + tail 
            + ",size=" + size);
      return r; 
   } 

   /** 
       Appends an object at the tail. 
       @param newValue the object to be appended 
       @precondition !isFull();
   */ 
   public void add(E newValue) 
   { 
      if (debug) System.out.print("add");
      elements[tail] = newValue; 
      if (debug) System.out.print(".");
      tail++;
      if (debug) System.out.print(".");
      size++;
      if (tail == elements.length) 
      {
         if (debug) System.out.print(".");
         tail = 0; 
      }
      if (debug) 
         System.out.println("head=" + head + ",tail=" + tail 
            + ",size=" + size);
   } 

   public boolean isFull() 
   { 
      return size == elements.length;
   } 

   public boolean isEmpty() 
   { 
      return size == 0; 
   } 

   public void setDebug(boolean newValue)
   {
      debug = newValue;
   }

   private Object[] elements; 
   private int head; 
   private int tail; 
   private int size;
   private boolean debug;
}
