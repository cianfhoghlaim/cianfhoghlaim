import java.awt.geom.*;

/**
   A UML class diagram.
*/
public class ClassDiagramGraph extends Graph
{

   public boolean connect(Edge e, Point2D p1, Point2D p2)
   {
      Node n1 = findNode(p1);
      Node n2 = findNode(p2);
      if (n1 == n2) return false;
      return super.connect(e, p1, p2);
   }

   public Node[] getNodePrototypes()
   {
      return new Node[] { new ClassNode() };
   }

   public Edge[] getEdgePrototypes()
   {
      ClassRelationshipEdge[] e = new ClassRelationshipEdge[6];

      e[0] = new ClassRelationshipEdge();
      e[0].setLineStyle(LineStyle.DOTTED);
      e[0].setEndArrowHead(ArrowHead.V);

      e[1] = new ClassRelationshipEdge();
      e[1].setBentStyle(BentStyle.VHV);
      e[1].setEndArrowHead(ArrowHead.TRIANGLE);

      e[2] = new ClassRelationshipEdge();
      e[2].setBentStyle(BentStyle.VHV);
      e[2].setLineStyle(LineStyle.DOTTED);
      e[2].setEndArrowHead(ArrowHead.TRIANGLE);

      e[3] = new ClassRelationshipEdge();
      e[3].setBentStyle(BentStyle.HVH);
      e[3].setEndArrowHead(ArrowHead.V);

      e[4] = new ClassRelationshipEdge();
      e[4].setBentStyle(BentStyle.HVH);
      e[4].setStartArrowHead(ArrowHead.DIAMOND);

      e[5] = new ClassRelationshipEdge();
      e[5].setBentStyle(BentStyle.HVH);
      e[5].setStartArrowHead(ArrowHead.BLACK_DIAMOND);

      return e;
  }
}





