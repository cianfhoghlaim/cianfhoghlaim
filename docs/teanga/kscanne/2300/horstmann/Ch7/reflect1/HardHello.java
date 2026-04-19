import java.lang.reflect.*;
import java.io.*;

/**
   This program prints "Hello, World" the hard way,
   using reflection.
*/
public class HardHello
{
   public static void main(String[] args)
      throws NoSuchMethodException, IllegalAccessException,
             InvocationTargetException
   {
      Method m = PrintStream.class.getDeclaredMethod(
            "println", String.class);
      m.invoke(System.out, "Hello, World!");
   }
}

