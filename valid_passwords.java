import java.io.*;
import java.util.*;
import java.text.*;
import java.math.*;
import java.util.regex.*;

class Solution {

    public static void main(String[] args) {
        /* Enter your code here. Read input from STDIN. Print output to STDOUT. Your class should be named Solution. */
        int no_test_cases;
        long million=(long)Math.pow(10,6);
        Scanner sc=new Scanner(System.in);
        no_test_cases=Integer.parseInt(sc.nextLine());
        String s;
        String str[];
        int min=0,max=0;
        long count=0;
        int while_loop_driver=0;
        for(int i=0;i<no_test_cases;i++){
            count=0;
            s=sc.nextLine();
            str=s.split(" ");
            min=Integer.parseInt(str[0]);
            max=Integer.parseInt(str[1]);
            while_loop_driver=min+1;
            //count=(long)Math.pow(10,min);
            /*while(count<million && while_loop_driver<=max ){
                count+=count*10;
                while_loop_driver++;
            }*/
            if(min >=6 || max>=6){
                System.out.println("YES");
            }
            else{
                System.out.println("NO");
            }
        }
    }
}