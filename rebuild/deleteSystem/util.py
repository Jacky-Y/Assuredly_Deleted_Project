import json

class NotificationTreeUtils:
    @staticmethod
    def find_all_nodes_except(json_tree, exclude_node, current_node=None, result=None):
        """
        查找除了指定节点外的所有其他节点。
        
        :param json_tree: 传播树的 JSON 对象。
        :param exclude_node: 要排除的节点。
        :param current_node: 当前遍历的节点。
        :param result: 用于存储结果的列表。
        :return: 所有除了指定节点外的其他节点的列表。
        """
        if result is None:
            result = []
        if current_node is None:
            current_node = list(json_tree.keys())[0]

        if current_node != exclude_node:
            result.append(current_node)

        children = json_tree.get(current_node, {}).get('children', [])
        for child in children:
            if isinstance(child, dict):
                for key in child.keys():
                    NotificationTreeUtils.find_all_nodes_except(child, exclude_node, key, result)
            elif child != exclude_node:
                result.append(child)

        return result

    @staticmethod
    def find_parent(json_tree, target_node, current_node=None, parent=None):
        """
        查找给定节点的父节点。
        
        :param json_tree: 传播树的 JSON 对象。
        :param target_node: 要查找父节点的目标节点。
        :param current_node: 当前遍历的节点。
        :param parent: 当前节点的父节点。
        :return: 目标节点的父节点。
        """
        # 如果是树的第一层，设置当前节点为根节点
        if current_node is None:
            current_node = list(json_tree.keys())[0]

        # 如果找到目标节点，返回父节点
        if current_node == target_node:
            return parent

        # 如果当前节点有子节点，递归遍历子节点
        children = json_tree.get(current_node, {}).get('children', [])
        for child in children:
            if isinstance(child, dict):
                # 子节点也是一个字典（有自己的子节点）
                for key in child.keys():
                    found_parent = NotificationTreeUtils.find_parent(child, target_node, key, current_node)
                    if found_parent is not None:
                        return found_parent
            elif child == target_node:
                # 直接找到目标节点
                return current_node

        return None

    @staticmethod
    def get_root_node(json_tree):
        return list(json_tree.keys())[0]

if __name__=="__main__":

    # 示例 JSON 字符串
    # json_str = '{"b1000": {"children": [{"b1001": {"children": ["b1002"]}}, {"b1003": {"children": ["b1004"]}}]}}'

    json_str = '{"b1000": {"children":[]}}'

    # 将 JSON 字符串转换为字典
    json_tree = json.loads(json_str)

    # 寻找目标节点的父节点
    target_node = 'b1000'
    # parent = find_parent(json_tree, target_node)
    parent=NotificationTreeUtils.find_parent(json_tree, target_node)
    others=NotificationTreeUtils.find_all_nodes_except(json_tree, target_node)
    root=NotificationTreeUtils.get_root_node(json_tree)



    print(f"源域: {root}")
    print(f"其他节点: {others}")
    print(f"{target_node} 的父节点: {parent}")
