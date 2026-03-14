import java.io.*;

/**
   A test class to demonstrate serialization of cyclic
   data structures.
*/
public class Employee implements Serializable
{
   /**
      Constructs an employee.
      @param name the employee name
      @param salary the employee salary
   */
   public Employee(String name, double salary)
   {
      this.name = name;
      this.salary = salary;
      this.buddy = this;
   }

   /**
      Sets the buddy of this employee
      @param buddy the new buddy
   */
   public void setBuddy(Employee buddy)
   {
      this.buddy = buddy;
   }

   public String toString()
   {
      return getClass().getName() 
         + "[name=" + name
         + ",salary=" + salary
         + ",buddy=" + buddy.name
         + "]";
   }

   private String name;
   private double salary;
   private Employee buddy;
}
