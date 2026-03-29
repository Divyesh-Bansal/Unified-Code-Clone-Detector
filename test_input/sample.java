// Sample Java file with duplicate/similar methods for testing

public class MathUtils {

    public int addNumbers(int a, int b) {
        int result = a + b;
        return result;
    }

    public int sumValues(int x, int y) {
        int total = x + y;
        return total;
    }

    public static void printArray(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            System.out.println(arr[i]);
        }
    }

    public static void displayArray(int[] data) {
        for (int j = 0; j < data.length; j++) {
            System.out.println(data[j]);
        }
    }

    private int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }

    protected double calculateAverage(int[] numbers) {
        double sum = 0;
        for (int i = 0; i < numbers.length; i++) {
            sum = sum + numbers[i];
        }
        return sum / numbers.length;
    }
}
