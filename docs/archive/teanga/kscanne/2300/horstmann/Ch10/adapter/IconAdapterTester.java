import java.awt.*;
import javax.swing.*;

/**
   This program demonstrates how an icon is adapted to
   a component. The component is added to a frame.
*/
public class IconAdapterTester
{
   public static void main(String[] args)
   {
      Icon icon = new CarIcon(300);
      JComponent component = new IconAdapter(icon);

      JFrame frame = new JFrame();
      frame.add(component, BorderLayout.CENTER);
      frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
      frame.pack();
      frame.setVisible(true);
   }
}
