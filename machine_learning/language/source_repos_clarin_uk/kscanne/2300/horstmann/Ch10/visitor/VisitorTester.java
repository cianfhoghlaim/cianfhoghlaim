import java.io.*;

public class VisitorTester
{
   public static void main(String[] args)
   {
      DirectoryNode node = new DirectoryNode(new File(".."));
      node.accept(new PrintVisitor());
   }   
}
