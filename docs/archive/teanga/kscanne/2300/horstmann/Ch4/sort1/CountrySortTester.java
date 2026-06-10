import java.util.*;

public class CountrySortTester
{
   public static void main(String[] args)
   {
      ArrayList<Country> countries = new ArrayList<Country>();
      countries.add(new Country("Uruguay", 176220));
      countries.add(new Country("Thailand", 514000));
      countries.add(new Country("Belgium", 30510));

      Collections.sort(countries);
      // Now the array list is sorted by area
      for (Country c : countries)
         System.out.println(c.getName() + " " + c.getArea());
   }
}
