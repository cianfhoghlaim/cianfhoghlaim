import java.awt.*;
import javax.swing.*;

/**
   An adapter that turns an icon into a JComponent.
*/
public class IconAdapter extends JComponent
{
   /**
      Constructs a JComponent that displays a given icon.
      @param icon the icon to display
   */
   public IconAdapter(Icon icon)
   {
      this.icon = icon;
   }

   public void paintComponent(Graphics g)
   {
      icon.paintIcon(this, g, 0, 0);
   }

   public Dimension getPreferredSize()
   {
      return new Dimension(icon.getIconWidth(),
            icon.getIconHeight());
   }

   private Icon icon;
}
