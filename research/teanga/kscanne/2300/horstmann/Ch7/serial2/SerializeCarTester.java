import java.io.*;

/**
   A program that serializes and deserializes a car.
*/
public class SerializeCarTester
{
   public static void main(String[] args)
         throws IOException, ClassNotFoundException
   {
      Car beemer = new Car(100, 100, 60);
      System.out.println(beemer);
      ObjectOutputStream out = new ObjectOutputStream(
            new FileOutputStream("fleet.dat"));
      out.writeObject(beemer);
      out.close();
      ObjectInputStream in = new ObjectInputStream(
            new FileInputStream("fleet.dat"));
      System.out.println(in.readObject());
      in.close();
   }
}
