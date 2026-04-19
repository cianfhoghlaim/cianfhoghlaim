import java.awt.Component;
import java.beans.PropertyEditorSupport;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.text.Document;

/**
   A property editor for the MultiLineString type.
*/
public class MultiLineStringEditor extends PropertyEditorSupport
{
   public boolean supportsCustomEditor()
   {
      return true;
   }

   public Component getCustomEditor()
   {
      final MultiLineString value = (MultiLineString) getValue();
      final JTextArea textArea = new JTextArea(value.getText(),10, 40);
      textArea.getDocument().addDocumentListener(new
         DocumentListener()
         {
            public void insertUpdate(DocumentEvent e)
            {
               value.setText(textArea.getText());
               firePropertyChange();
            }
            public void removeUpdate(DocumentEvent e)
            {
               value.setText(textArea.getText());
               firePropertyChange();
            }
            public void changedUpdate(DocumentEvent e)
            {
            }
         });
      return new JScrollPane(textArea);
   }
}
