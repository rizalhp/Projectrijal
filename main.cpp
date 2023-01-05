#include "tree.h"

int main(){
     cout << "=========================================================" << endl;
     adrNode root = nil;
     int x[9] = {5,3,9,10,4,7,1,8,6};
     /* Tampilkan isi dari array */
    for (int i=0; i<9; i++){
        cout << x[i] << " ";
    }
     /* 1. Tambahkan setiap elemen array x kedalam BST secara berurutan */
     /* sehingga dihasilkan BST seperti Gambar 1, gunakan looping*/
     for (int i=0; i<9; i++){
        adrNode P = newNode1301213444(x[i]);
        insertNode1301213444(root, P);
     }
     /* 2. Tampilkan node dari BST secara Pre-Order */
     printf("\n");
     printf("\nPre Order\t\t: ");
     printPreOrder1301213444(root);

     /* 3. Tampilkan keturunan dari node 9*/
     printf("\n");
     printf("\nDescendent of Node 9\t: ");
     printDescendant1301213444(root, 9);

     /* 4. Tampilkan total info semua node pada BST */
     printf("\n");
     printf("\nSum of BST Info\t\t: ");
     cout << sumNode1301213444(root);

     /* 5. Tampilkan banyaknya daun dari BST */
     printf("\nNumber of Leaves\t: ");
     cout << countLeaves1301213444(root);

     /* 4. Tampilkan Tinggi dari Tree*/
     printf("\nHeight of Tree\t\t: ");
     cout << heightTree1301213444(root)-1;
     cout << endl <<"=========================================================";
     return 0;
}
