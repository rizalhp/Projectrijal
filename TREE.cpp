#include "TREE.h"

adrNode newNode1301213444(infotype x){
    adrNode P = new node;

    data(P) = x;
    P->left = nil;
    P->right = nil;

    return P;
}

adrNode findNode1301213444(adrNode root, infotype x){
    if (root == nil){
        return nil;
    }else if(data(root) == x){
        return root;
    }

    adrNode P = findNode1301213444(root->left, x);
    if (P!=nil){
        return P;
    }
    return findNode1301213444(root->right, x);
}

void insertNode1301213444(adrNode &root, adrNode P){
    if (root == nil){
        root = P;
    }else if (data(P) < data(root)){
        insertNode1301213444(root->left, P);
    }else {
        insertNode1301213444(root->right, P);
    }
}

void printPreOrder1301213444(adrNode root){
    if (root != nil) {
        cout << data(root) << " ";
        printPreOrder1301213444(root->left);
        printPreOrder1301213444(root->right);
    }
}
void printDescendant1301213444(adrNode root, infotype x){
    adrNode P = findNode1301213444(root, x);
    if (P == nil){
        cout << "TREE KOSONG!!!" << endl;
    }
    printPreOrder1301213444(P->left);
    printPreOrder1301213444(P->right);
}

int sumNode1301213444(adrNode root){
    if (root != nil){
        return data(root) + sumNode1301213444(root->left) + sumNode1301213444(root->right);
    }
    return 0;
}
int countLeaves1301213444(adrNode root){

    if (root == nil){
        return nil;
    }else if (root->left == nil && root->right == nil){
        return 1;
    }
    return countLeaves1301213444(root->left) + countLeaves1301213444(root->right);
}

int heightTree1301213444(adrNode root){
    if (root == nil){
        return nil;
    }
    int leftH = heightTree1301213444(root->left);
    int rightH = heightTree1301213444(root->right);

    return max(leftH, rightH) + 1;
}
