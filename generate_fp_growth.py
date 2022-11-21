import time
import os

from numpy import spacing

from generate_tree_node import *
from collections import defaultdict
import matplotlib.pylab as plt


def generate_freq_item_sets(input_transactions, minimum_support):
    """
    This function takes input transactions and minimum support:
    1. Create item-sets each transaction and filters it out based on the minimum support value.
    2. The Transaction list is then filtered and sorted based on the frequency of the items present in it.
    3. Create a main/first FP tree based on the filtered transactions.
    4. Create a route table for each item based on the main FP tree.
    5. Create a conditional database for each item in the route table and return the frequent item sets
    6. Call the conditional database function recursively for all the subtrees generated suing conditional DB.

    :param input_transactions: Pass all the transactions from the input file. It is a list of items list.
    :param minimum_support: Ask user to give the desired minimum support value to calculate the freq items
    :return: Return the freq item sets with the frequency of occurrence.
    """
    # Create item_sets dictionary and initiate all the values to zero
    item_sets = defaultdict(lambda: 0)

    # Fill the item set with all the values from the transactions
    for txn in input_transactions:
        for each_column in txn:
            item_sets[each_column] += 1

    temp_list = []
    # Filter out all the items that do not meet the minimum support requirement.
    for each_item, count in item_sets.items():
        if int(count) >= minimum_support:
            item_sets[each_item] = count
        else:
            temp_list.append(each_item)

    for it in temp_list:
        del item_sets[it]

    def order_transactions(each_transaction):
        """
        1. This function will take transaction as an input and update it by removing
            the infrequent items
        2. It also sorts the items in the transaction in decreasing order of the count.
        3. It will then return the filtered transaction.
        :param each_transaction: Pass single transaction from the transaction list
        :return: Return the sorted and filtered transaction
        """
        for each_element in each_transaction:
            if each_element not in item_sets:
                each_transaction.remove(each_element)
        each_transaction = sorted(each_transaction, key=lambda v: item_sets[v], reverse=True)
        return each_transaction

    # Create the main FP tree using all the filtered transactions and name it as first_fp_tree.
    # Create a empty FR tree initially and add the all the transactions into the tree using
    # fp_tree.add() function
    first_fp_tree = fp_tree()
    for transaction in list(map(order_transactions, input_transactions)):
        first_fp_tree.append_items(transaction)

    def conditional_db(tree, retrieved_list):
        """
        1. First we list all the items from the route table of the tree passed.
        2. Calculate the current support of the nodes corresponding to the above items.
        3. Check for the minimum support of the items.
        4. If the items does not satisfy the minimum support, continue and check foe next item.
        5. Else if items satisfy the minimum support, generate the parent paths of the item and
            create a new conditional FP tree for the parent paths.
        6. Call the conditional DB function for the new conditional FP tree recursively.
        7. Return the frequent items for all the recursive calls.
        :param tree: Pass the FP tree
        :param retrieved_list: Pass the retrieved list
        :return: return the frequency item sets
        """
        # get the items and nodes corresponding to each item in the route table.
        for route_table_item, nodes in tree.get_items():
            # get the current support for each item in the route table.
            curr_support = 0
            for n in nodes:
                curr_support += n.count

            # Check if the current support satisfies the minimum support value.
            if curr_support < minimum_support or route_table_item in retrieved_list:
                continue

            # generate the parent paths of the item and
            # create a new conditional FP tree for the parent paths.
            else:
                # Yield the frequent item sets with their current support to the caller.
                freq_item_set = [route_table_item] + retrieved_list
                yield (freq_item_set, curr_support)

                # Get all the prefix paths for the route table item using get_parent_paths() function
                parent_paths = tree.get_parent_paths(route_table_item)

                # Form conditional tree from the prefix paths of the route table item
                # Create an empty tree initially
                cond_tree = fp_tree()
                cond_item = None

                # Add all the nodes from the prefix paths to the conditional FP tree
                for curr_path in parent_paths:
                    # initialize the conditional item to the last item in the prefix path.
                    if cond_item is None:
                        cond_item = curr_path[-1].item

                    # assign a pointer to the root of the conditional FP tree
                    tree_pointer = cond_tree.root
                    for node in curr_path:
                        # check if the node is already existing in the conditional FP tree
                        next_point = tree_pointer.find(node.item)

                        # If the node already exists in the conditional tree, move pointer
                        # to the current node
                        if next_point:
                            tree_pointer = next_point
                            continue

                        # if the current node doesn't exist, create a new node with the item
                        # and add it to the conditional FP tree.
                        else:
                            # Assign the count for the node only if the node is pointing to the
                            # conditional item, else assign the count to zero.
                            if node.item == cond_item:
                                current_count = node.count
                            else:
                                current_count = 0
                            next_point = fp_node(cond_tree, node.item, current_count)
                            tree_pointer.add_node(next_point)
                            # Update the node to the route table
                            cond_tree.revise_route_table(next_point)
                        tree_pointer = next_point

                # Update the count for each node in the conditional FP tree.
                for curr_path in cond_tree.get_parent_paths(cond_item):
                    current_count = curr_path[-1].count
                    # The count for the conditional item node is already updated above.
                    for node in reversed(curr_path[:-1]):
                        node._count += current_count

                # Call the conditional_db function for the conditional FP tree created above.
                # Note: This method is called recursively for every conditional FP tree created.
                for freq_sets in conditional_db(cond_tree, freq_item_set):
                    yield freq_sets

    for freq_item_sets in conditional_db(first_fp_tree, []):
        yield freq_item_sets


# Function to generate bar plots
def bar_plot(dict, values, keys, x_label, y_label):
    plt.bar(range(len(dict)), list(values), tick_label=list(keys))
    xlocs, xlabs = plt.xticks()
    plt.title(x_label + ' vs ' + y_label)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    for i, v in enumerate(values):
        plt.text(xlocs[i] - 0.25, v + 0.01, str(v))
    # plt.show()
    plt.savefig(f'Outputs/{outfolder}/{y_label}.png')
    plt.clf()


# Function to generate line plots
def line_plot(keys, values, x_label, y_label):
    plt.plot(keys, values, marker='x')
    plt.title(x_label + ' vs ' + y_label)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # plt.show()
    plt.savefig(f'Outputs/{outfolder}/{y_label}.png')
    plt.clf()



if __name__ == "__main__":
    import csv
    import tracemalloc

    # Create an empty list of transactions.
    transactions = []
    minsup = [100,200,500,700,1000,2000,5000,10000,15000]  # input('Enter Minimum support(value>2): ')
    dir = 'benchmarks/adult.csv'  # input("Enter directory Path(examples/filename.csv): ")

    outfolder = dir.partition('/')[2].partition('.')[0] + '_FreqItemsets'
    parent_dir = "Outputs/"

    # Path
    path = os.path.join(parent_dir, outfolder)

    # Creating the path if doesnt exist in project folder
    if not os.path.exists(path):
        os.mkdir(path)

    if dir == 'benchmarks/page-blocks.csv':
        with open(dir) as csv_file:
            for row in csv.reader(csv_file):
                for i in row:
                    i = " ".join(i.split()).split(' ')
                    transactions.append(i)
    elif dir == 'benchmarks/bank-additional-full.csv':
        with open(dir) as csv_file:
            for row in csv.reader(csv_file):
                for i in row:
                    i = ";".join(i.split()).split(';')
                    transactions.append(i)
    else:
        with open(dir) as csv_file:
            for row in csv.reader(csv_file):
                if row:
                    transactions.append(row)


    # Removing the empty values from transactions
    for item in transactions:
        while '' in item:
            item.remove('')
        for i in item:
            if '?' in i:
                item.remove(i)
            if '"' in i:
                i=i.replace('"','')

    print('Total Transactions from DataSet:', len(transactions), ' and attributes:', len(transactions[0]))

    # Calculating memory, time_elapsed, itemsets generated for each minimum support value
    time_elapsed = {}
    memory_usage = {}
    itemsets_generated = {}
    for minSupport in minsup:
        result = []
        tick = time.time()
        tracemalloc.start()
        for itemset, support in generate_freq_item_sets(transactions, int(minSupport)):
            result.append((itemset, support))

        result = sorted(result, key=lambda i: i[1], reverse=True)
        tock = time.time()
        memory_usage[minSupport] = tracemalloc.get_traced_memory()[0]
        time_elapsed[minSupport] = round((tock - tick) * 1000, 2)
        itemsets_generated[minSupport] = len(result)
        #print(result)
        with open(f"Outputs/{outfolder}/FreqItemsets_{minSupport}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            data = [f"Frequent itemset for MinSupport of {minSupport}", "Frequency"]
            writer.writerow(data)

            writer.writerows(result)

        print('Number of Frequent itemSets generated for minSupport', minSupport, len(result))
        print('\n')

print('Minimum Supports', minsup)
print('Time elapsed:', time_elapsed, '\n')
print('Peak Memory Usage:', memory_usage, '\n')
print('Itemsets Generated:', itemsets_generated, '\n')
table_path = dir.partition('/')[2].partition('.')[0]
with open(f'Outputs/{outfolder}/Tables_{table_path}.csv', 'w') as f:
    data = ["Minimum Support", "Time Elapsed(ms)"]
    writer = csv.writer(f)
    writer.writerow(data)
    for key in time_elapsed.keys():
        f.write("%s,%s\n" % (key, time_elapsed[key]))
    writer.writerow('')
    data = ["Minimum Support", "Memory usage(bytes)"]
    writer = csv.writer(f)
    writer.writerow(data)
    for key in memory_usage.keys():
        f.write("%s,%s\n" % (key, memory_usage[key]))
    writer.writerow('')
    data = ["Minimum Support", "Frequent Itemsets Generated"]
    writer = csv.writer(f)
    writer.writerow(data)
    for key in itemsets_generated.keys():
        f.write("%s,%s\n" % (key, itemsets_generated[key]))

bar_plot(time_elapsed, time_elapsed.values(), time_elapsed.keys(), 'Minimum Support', 'Time elapsed in ms')
# bar_plot(memory_usage,memory_usage.values(),memory_usage.keys(),'Minimum Support','Memory Usage')
bar_plot(itemsets_generated, itemsets_generated.values(), itemsets_generated.keys(), 'Minimum Support',
         'Itemsets Generated')

line_plot(itemsets_generated.keys(), itemsets_generated.values(), 'Minimum support', 'Itemsets Generated(Line)')
line_plot(memory_usage.keys(), memory_usage.values(), 'Minimum support', 'Memory Usage')

print(f'Access the folder "Outputs/{outfolder}" for the FrequentItemsets generated, Tables and plots.')
