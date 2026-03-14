import java.awt.event.*;
import javax.swing.*;

/**
   This action places a greeting into a text field 
   and afterwards disables itself and enables its 
   opposite action.
*/
public class GreetingAction extends AbstractAction
{
   /**
      Constructs a greeting action.
      @param greeting the string to add to the text area
      @param textArea the text area to which to add the greeting
   */      
   public GreetingAction(String greeting, JTextArea textArea)
   {
      this.greeting = greeting;
      this.textArea = textArea;
   }

   /**
      Sets the opposite action.
      @param action the action to be enabled after this action was
      carried out
   */
   public void setOpposite(Action action)
   {
      oppositeAction = action;
   }

   public void actionPerformed(ActionEvent event)
   {
      textArea.append(greeting);
      textArea.append("\n");
      if (oppositeAction != null)
      {
         setEnabled(false);
         oppositeAction.setEnabled(true);
      }
   }

   private String greeting;
   private JTextArea textArea;
   private Action oppositeAction;
}
