import java.awt.Dimension;
import java.awt.Frame;
import java.awt.Toolkit;
import javax.swing.JFrame;

/**
   A program for editing UML diagrams.
*/
public class UMLEditor
{
   public static void main(String[] args)
   {
      JFrame frame = new GraphFrame(new ClassDiagramGraph());
      frame.setVisible(true);
   }
}

