import java.awt.*;
import javax.swing.*;

/**
   This program demonstrates action objects. Two actions
   insert greetings into a text area. Each action can be
   triggered by a menu item or toolbar button. When an
   action is carried out, the opposite action becomes enabled.
*/
public class CommandTester
{
   public static void main(String[] args)
   {
      JFrame frame = new JFrame();
      JMenuBar bar = new JMenuBar();
      frame.setJMenuBar(bar);
      JMenu menu = new JMenu("Say");
      bar.add(menu);
      JToolBar toolBar = new JToolBar();
      frame.add(toolBar, BorderLayout.NORTH);
      JTextArea textArea = new JTextArea(10, 40);
      frame.add(textArea, BorderLayout.CENTER);

      GreetingAction helloAction = new GreetingAction(
            "Hello, World", textArea);
      helloAction.putValue(Action.NAME, "Hello");
      helloAction.putValue(Action.SMALL_ICON,
         new ImageIcon("hello.png"));

      GreetingAction goodbyeAction = new GreetingAction(
            "Goodbye, World", textArea);
      goodbyeAction.putValue(Action.NAME, "Goodbye");
      goodbyeAction.putValue(Action.SMALL_ICON,
            new ImageIcon("goodbye.png"));

      helloAction.setOpposite(goodbyeAction);
      goodbyeAction.setOpposite(helloAction);
      goodbyeAction.setEnabled(false);

      menu.add(helloAction);
      menu.add(goodbyeAction);

      toolBar.add(helloAction);
      toolBar.add(goodbyeAction);

      frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
      frame.pack();
      frame.setVisible(true);
   }
}
