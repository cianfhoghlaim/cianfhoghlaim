import java.awt.*;
import javax.swing.*;

public class ScrollPaneTester
{
   public static void main(String[] args)
   {
      JFrame frame = new JFrame();

      JTextArea area = new JTextArea(20, 40); // 20 rows, 40 columns
      JScrollPane scroller = new JScrollPane(area);
      frame.add(scroller, BorderLayout.CENTER);

      frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
      frame.setSize(200, 200);
      frame.setVisible(true);
   }
}

