/**
   The common interface for file and directory nodes.
*/
public interface FileSystemNode
{
   void accept(FileSystemVisitor v);
}
