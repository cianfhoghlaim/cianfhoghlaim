import java.util.*;

/**
   This class carries out the merge sort algorithm.
*/
public class MergeSorter
{
   /**
      Sorts an array, using the merge sort algorithm.
      @param a the array to sort
      @param comp the comparator to compare array elements
   */
   public static <E> void sort(E[] a, Comparator<? super E> comp)
   {
      mergeSort(a, 0, a.length - 1, comp);
   }

   /**
      Sorts a range of an array, using the merge sort
      algorithm.
      @param a the array to sort
      @param from the first index of the range to sort
      @param to the last index of the range to sort
      @param comp the comparator to compare array elements
   */
   private static <E> void mergeSort(E[] a, int from, int to,
      Comparator<? super E> comp)
   {
      if (from == to) return;
      int mid = (from + to) / 2;
      // Sort the first and the second half
      mergeSort(a, from, mid, comp);
      mergeSort(a, mid + 1, to, comp);
      merge(a, from, mid, to, comp);
   }

   /**
      Merges two adjacent subranges of an array
      @param a the array with entries to be merged
      @param from the index of the first element of the
         first range
      @param mid the index of the last element of the
         first range
      @param to the index of the last element of the
         second range
      @param comp the comparator to compare array elements
   */
   private static <E> void merge(E[] a,
      int from, int mid, int to, Comparator<? super E> comp)
   {
      int n = to - from + 1;
         // Size of the range to be merged

      // Merge both halves into a temporary array b
      Object[] b = new Object[n];

      int i1 = from;
         // Next element to consider in the first range
      int i2 = mid + 1;
         // Next element to consider in the second range
      int j = 0;
         // Next open position in b

      // As long as neither i1 nor i2 past the end, move
      // the smaller element into b
      while (i1 <= mid && i2 <= to)
      {
         if (comp.compare(a[i1], a[i2]) < 0)
         {
            b[j] = a[i1];
            i1++;
         }
         else
         {
            b[j] = a[i2];
            i2++;
         }
         j++;
      }

      // Note that only one of the two while loops
      // below is executed

      // Copy any remaining entries of the first half
      while (i1 <= mid)
      {
         b[j] = a[i1];
         i1++;
         j++;
      }

      // Copy any remaining entries of the second half
      while (i2 <= to)
      {
         b[j] = a[i2];
         i2++;
         j++;
      }

      // Copy back from the temporary array
      for (j = 0; j < n; j++)
         a[from + j] = (E) b[j];
   }
}
