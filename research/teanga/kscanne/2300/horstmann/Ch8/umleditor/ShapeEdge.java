import java.awt.BasicStroke;
import java.awt.Graphics2D;
import java.awt.Shape;
import java.awt.geom.Line2D;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;

/**
   A class that assumes that an edge can yield its shape
   and then takes advantage of the fact that containment testing can 
   be done by stroking the shape with a fat stroke.
*/
public abstract class ShapeEdge extends AbstractEdge
{  
   /**
      Returns the path that should be stroked to
      draw this edge. The path does not include
      arrow tips or labels.
      @return a path along the edge
   */
   public abstract Shape getShape();

   public Rectangle2D getBounds(Graphics2D g2)
   {
      return getShape().getBounds();
   }

   public boolean contains(Point2D aPoint)
   {
      final double MAX_DIST = 3;

      // the end points may contain small nodes, so don't
      // match them
      Line2D conn = getConnectionPoints();
      if (aPoint.distance(conn.getP1()) <= MAX_DIST 
         || aPoint.distance(conn.getP2()) <= MAX_DIST)
         return false;

      Shape p = getShape();
      BasicStroke fatStroke = new BasicStroke(
         (float)(2 * MAX_DIST));
      Shape fatPath = fatStroke.createStrokedShape(p);
      return fatPath.contains(aPoint);
   }
}
