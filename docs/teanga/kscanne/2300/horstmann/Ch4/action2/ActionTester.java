import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class ActionTester
{
   public static void main(String[] args)
   {
      JFrame frame = new JFrame();

      final int FIELD_WIDTH = 20;
      textField = new JTextField(FIELD_WIDTH);
      textField.setText("Click a button!");

      JButton helloButton = new JButton("Say Hello");

      helloButton.addActionListener(
         createGreetingButtonListener("Hello, World!"));

      JButton goodbyeButton = new JButton("Say Goodbye");

      goodbyeButton.addActionListener(
         createGreetingButtonListener("Goodbye, World!"));

      frame.setLayout(new FlowLayout());

      frame.add(helloButton);
      frame.add(goodbyeButton);
      frame.add(textField);

      frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
      frame.pack();
      frame.setVisible(true);
   }

   public static ActionListener createGreetingButtonListener(
      final String message)
   {
      return new
         ActionListener()
         {
            public void actionPerformed(ActionEvent event)
            {
               textField.setText(message);
            }
         };
   }

   private static JTextField textField;
}
