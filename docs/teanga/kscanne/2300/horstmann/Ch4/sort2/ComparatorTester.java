import java.util.*;

public class ComparatorTester
{
   public static void main(String[] args)
   {
      ArrayList<Country> countries = new ArrayList<Country>();
      countries.add(new Country("Uruguay", 176220));
      countries.add(new Country("Thailand", 514000));
      countries.add(new Country("Belgium", 30510));
      Comparator<Country>  comp = new CountryComparatorByName();
      Collections.sort(countries, comp);
         // Now the array list is sorted by country name
      for (Country c : countries)
        System.out.println(c.getName() + " " + c.getArea());
   }
}

