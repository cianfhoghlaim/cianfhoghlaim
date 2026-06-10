import junit.framework.*;

/**
   A class to test the Day class with JUnit.
*/
public class DayTest extends TestCase
{
   /**
      This test tests the addDays method with positive 
      parameters.
   */
   public void testAdd()
   {
      for (int i = 1; i <= MAX_DAYS; i = i * INCREMENT)
      {
         Day d1 = new Day(1970, 1, 1);
         Day d2 = d1.addDays(i);
         assertTrue(d2.daysFrom(d1) == i);      
      }
   }

   /**
      This test tests the addDays method with negative 
      parameters.
   */
   public void testAddNegative()
   {
      for (int i = 1; i <= MAX_DAYS; i = i * INCREMENT)
      {
         Day d1 = new Day(1970, 1, 1);
         Day d2 = d1.addDays(-i);
         assertTrue(d1.daysFrom(d2) == i);      
      }
   }

   /**
      This test tests the daysFrom method.
   */
   public void testDaysFrom()
   {
      Day d1 = new Day(1970, 1, 1);
      Day d2 = new Day(2001, 1, 1);
      int n = d1.daysFrom(d2);
      Day d3 = d2.addDays(n);
      assertTrue(d1.getYear() == d3.getYear());      
      assertTrue(d1.getMonth() == d3.getMonth());      
      assertTrue(d1.getDate() == d3.getDate());      
   }

   /**
      This test tests arithmetic around the Gregorian
      calendar change.
   */
   public void testGregorianBoundary()
   {
      Day d1 = new Day(1580, 1, 1);
      Day d2 = d1.addDays(MAX_DAYS);
      Day d3 = d2.addDays(-MAX_DAYS);
      assertTrue(d3.daysFrom(d1) == 0);      
   }

   private static final int MAX_DAYS = 10000;
   private static final int INCREMENT = 10;
}

