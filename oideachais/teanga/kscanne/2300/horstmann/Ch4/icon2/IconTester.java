import javax.swing.*;

public class IconTester
{
   public static void main(String[] args)
   {
      JOptionPane.showMessageDialog(
            null, 
            "Hello, Mars!",
            "Message",
            JOptionPane.INFORMATION_MESSAGE,
            new MarsIcon(50));
      System.exit(0);
   }
}

