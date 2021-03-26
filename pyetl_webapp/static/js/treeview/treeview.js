private void PopulateTreeView_WithFiles(DirectoryInfo dirInfo, TreeView treeView, TreeNode treeNode)
{
    DirectoryInfo directory = dirInfo;
    if (directory.Name != null) {
        TreeNode directoryNode = new TreeNode
        {
            Text = directory.Name,
                Value = directory.FullName
        };
        if (treeNode == null) {
            //If Root Node, add to TreeView.
            treeView.Nodes.Add(directoryNode);
        }
        else {
            //If Child Node, add to Parent Node.
            treeNode.ChildNodes.Add(directoryNode);
        }

        //Get all files in the Directory.
        foreach(FileInfo file in directory.GetFiles())
        {
            //Add each file as Child Node.
            TreeNode fileNode = new TreeNode
            {
                Text = file.Name,
                    //Value = file.FullName,
                    Value = file.FullName,
                    Target = "_blank",
                    NavigateUrl = (new Uri(Server.MapPath("~/"))).MakeRelativeUri(new Uri(file.FullName).ToString()

                };
            directoryNode.ChildNodes.Add(fileNode);
        }

        directoryNode.CollapseAll();
        PopulateTreeView_WithDirectories(directory, treeView, directoryNode);
    }
}
