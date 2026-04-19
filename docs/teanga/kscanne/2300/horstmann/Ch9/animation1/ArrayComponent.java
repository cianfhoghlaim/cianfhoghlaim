import java.awt.*;
import java.awt.geom.*;
import javax.swing.*;

/**
   This component draws an array and marks two elements in the
   array.
*/
public class ArrayComponent extends JComponent
{
   public synchronized void paintComponent(Graphics g)
   {
      if (values == null) return;
      Graphics2D g2 = (Graphics2D) g;
      int width = getWidth() / values.length;
      for (int i = 0; i < values.length; i++)
      {
         Double v =  values[i];
         Rectangle2D bar = new Rectangle2D.Double(
            width * i, 0, width, v);
         if (v == marked1 || v == marked2)
            g2.fill(bar);
         else
            g2.draw(bar);
      }
   }

   /**
      Sets the values to be painted.
      @param values the array of values to display
      @param marked1 the first marked element
      @param marked2 the second marked element
   */
   public synchronized void setValues(Double[] values,
      Double marked1, Double marked2)
   {
      this.values = (Double[]) values.clone();
      this.marked1 = marked1;
      this.marked2 = marked2;
      repaint();
   }

   private Double[] values;
   private Double marked1;
   private Double marked2;
}
