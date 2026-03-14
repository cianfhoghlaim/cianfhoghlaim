import java.awt.*;
import java.awt.geom.*;
import java.awt.event.*;
import javax.swing.*;

/**
   A program that allows users to move a car with the mouse.
*/
public class CarMover
{
   public static void main(String[] args)
   {
      JFrame frame = new JFrame();
      frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

      frame.add(new CarComponent());
      frame.setSize(FRAME_WIDTH, FRAME_HEIGHT);
      frame.setVisible(true);
   }

   private static final int FRAME_WIDTH = 400;
   private static final int FRAME_HEIGHT = 400;
}


