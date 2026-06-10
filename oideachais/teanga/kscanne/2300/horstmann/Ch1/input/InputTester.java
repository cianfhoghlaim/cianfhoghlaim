import java.util.Scanner;

public class InputTester
{
   public static void main(String[] args)
   {
      Scanner in = new Scanner(System.in);
      System.out.print("How old are you?");
      int age = in.nextInt();
      age++;
      System.out.println("Next year, you'll be " + age);
   }
}
