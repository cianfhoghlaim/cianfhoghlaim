public class DayTester
{
   public static void main(String[] args)
   {
      Day today = new Day(2001, 2, 3); // February 3, 2001
      Day later = today.addDays(999);
      System.out.println(later.getYear() 
            + "-" + later.getMonth() 
            + "-" + later.getDate()); 
      System.out.println(later.daysFrom(today)); // Prints 999
   }
}
