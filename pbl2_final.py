from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QInputDialog
)
import sys

class Node:
    def __init__(self, eng_word, fr_word):
        self.eng_word = eng_word
        self.fr_word = fr_word
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, eng_word, fr_word):
        if self.root is None:
            self.root = Node(eng_word, fr_word)
        else:
            self._insert(self.root, eng_word, fr_word)

    def _insert(self, node, eng_word, fr_word):
        if (eng_word < node.eng_word) or (eng_word == node.eng_word and fr_word < node.fr_word):
            if node.left is None:
                node.left = Node(eng_word, fr_word)
            else:
                self._insert(node.left, eng_word, fr_word)
        else:
            if node.right is None:
                node.right = Node(eng_word, fr_word)
            else:
                self._insert(node.right, eng_word, fr_word)

    def search_eng(self, eng_word):
        return self._search_eng(self.root, eng_word)

    def _search_eng(self, node, eng_word):
        if node is None:
            return None
        if eng_word == node.eng_word:
            return node
        elif eng_word < node.eng_word:
            return self._search_eng(node.left, eng_word)
        else:
            return self._search_eng(node.right, eng_word)

    def search_fr(self, fr_word):
        return self._search_fr(self.root, fr_word)

    def _search_fr(self, node, fr_word):
        if node is None:
            return None
        if node.fr_word == fr_word:
            return node
        left_result = self._search_fr(node.left, fr_word)
        return left_result if left_result else self._search_fr(node.right, fr_word)

    def get_successor(self, node):
        if node.right:
            current = node.right
            while current.left:
                current = current.left
            return current
        return None

    def get_predecessor(self, node):
        if node.left:
            current = node.left
            while current.right:
                current = current.right
            return current
        return None

    def delete(self, eng_word):
        self.root = self._delete(self.root, eng_word)

    def _delete(self, node, eng_word):
        if node is None:
            return node
        if eng_word < node.eng_word:
            node.left = self._delete(node.left, eng_word)
        elif eng_word > node.eng_word:
            node.right = self._delete(node.right, eng_word)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            successor = self.get_successor(node)
            node.eng_word = successor.eng_word
            node.fr_word = successor.fr_word
            node.right = self._delete(node.right, successor.eng_word)
        return node

    def load_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        eng, fr = parts[0].strip(), parts[1].strip()
                        self.insert(eng, fr)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load file: {str(e)}")
            return False

    def save_to_file(self, filename):
        try:
            with open(filename, 'w') as file:
                for eng, fr in self._in_order_traversal():
                    file.write(f"{eng},{fr}\n")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save file: {str(e)}")
            return False

    def _in_order_traversal(self):
        result = []
        self._in_order(self.root, result)
        return result

    def _in_order(self, node, result):
        if node:
            self._in_order(node.left, result)
            result.append((node.eng_word, node.fr_word))
            self._in_order(node.right, result)

class TranslationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.bst = BST()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setWindowTitle("TOEICKilla Translation Tool")
        self.resize(400, 300)

        self.load_btn = QPushButton("Load Dictionary", self)
        self.translate_btn = QPushButton("Translate Word", self)
        self.add_btn = QPushButton("Add/Modify Entry", self)
        self.delete_btn = QPushButton("Delete Entry", self)
        self.save_btn = QPushButton("Save Dictionary", self)

        self.load_btn.clicked.connect(self.load_dictionary)
        self.translate_btn.clicked.connect(self.translate_word)
        self.add_btn.clicked.connect(self.add_modify_entry)
        self.delete_btn.clicked.connect(self.delete_entry)
        self.save_btn.clicked.connect(self.save_dictionary)

        layout.addWidget(self.load_btn)
        layout.addWidget(self.translate_btn)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    def load_dictionary(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Dictionary", "", "Text Files (*.txt)")
        if filename and self.bst.load_from_file(filename):
            QMessageBox.information(self, "Success", "Dictionary loaded successfully!")

    def translate_word(self):
        word, ok = QInputDialog.getText(self, "Translation", "Enter a word to translate:")
        if ok and word:
            node = self.bst.search_eng(word) or self.bst.search_fr(word)
            if node:
                translation = node.fr_word if word == node.eng_word else node.eng_word
                QMessageBox.information(self, "Translation", f"Translation: {translation}")
            else:
                QMessageBox.warning(self, "Not Found", "Word is not in dictionary!")

    def add_modify_entry(self):
        eng, ok1 = QInputDialog.getText(self, "New Entry", "Enter an English word:")
        if ok1 and eng:
            fr, ok2 = QInputDialog.getText(self, "New Entry", "Enter a French translation:")
            if ok2 and fr:
                if self.bst.search_eng(eng):
                    self.bst.delete(eng)
                self.bst.insert(eng, fr)
                QMessageBox.information(self, "Success", "Entry updated successfully!")

    def delete_entry(self):
        word, ok = QInputDialog.getText(self, "Delete Entry", "Enter an English word to delete:")
        if ok and word:
            if self.bst.search_eng(word):
                self.bst.delete(word)
                QMessageBox.information(self, "Success", "Entry deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Word not found in dictionary!")

    def save_dictionary(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Dictionary", "", "Text Files (*.txt)")
        if filename and self.bst.save_to_file(filename):
            QMessageBox.information(self, "Success", "Dictionary saved successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslationApp()
    window.show()
    sys.exit(app.exec_())