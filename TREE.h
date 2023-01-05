#ifndef TREE_H_INCLUDED
#define TREE_H_INCLUDED
#include <iostream>
#define nil NULL
#define data(P) P->data
using namespace std;

struct node{
    node *left;
    node *right;
    int data;
};
typedef node *adrNode;
typedef int infotype;

adrNode newNode1301213444(infotype x);
adrNode findNode1301213444(adrNode root, infotype x);
void insertNode1301213444(adrNode &root, adrNode P);
void printPreOrder1301213444(adrNode root);
void printDescendant1301213444(adrNode root, infotype x);
int sumNode1301213444(adrNode root);
int countLeaves1301213444(adrNode root);
int heightTree1301213444(adrNode root);

#endif // TREE_H_INCLUDED
