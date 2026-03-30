import java.io.*;

/**
   A program that serializes and deserializes an Employee array.
*/
public class SerializeEmployeeTester
{
   public static void main(String[] args)
         throws IOException, ClassNotFoundException
   {
      Employee[] staff = new Employee[2];
      staff[0] = new Employee("Fred Flintstone", 50000);
      staff[1] = new Employee("Barney Rubble", 60000);
      staff[0].setBuddy(staff[1]);
      staff[1].setBuddy(staff[0]);
      ObjectOutputStream out = new ObjectOutputStream(
            new FileOutputStream("staff.dat"));
      out.writeObject(staff);
      out.close();
      ObjectInputStream in = new ObjectInputStream(
            new FileInputStream("staff.dat"));
      Employee[] staff2 = (Employee[]) in.readObject();
      in.close();
      for (Employee e : staff2)
         System.out.println(e);
   }
}
