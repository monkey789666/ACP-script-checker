# import matplotlib
# matplotlib.use('Agg')
import tkinter as tk
from os.path import basename



def select_file():
    from tkinter.filedialog import askopenfilename
    from os.path import expanduser
    filewindow = tk.Tk()
    filewindow.withdraw()
    filename = askopenfilename(initialdir=expanduser('~\\Documents\\ACP Astronomy\\Plans'))
    # filename = './gyver.txt'
    filewindow.destroy()
    return filename

def get_script():
    with open(filename, 'r') as f:
        script_lines = f.readlines()

    targets = {
        'obj_name': [],
        'index': [],
        'oneline': [],
        'check': [],
    }
    chain = {
        'line': [],
        'check': [],
        'index': [],
    }
    string_list = []
    i = 0

    for line in script_lines:
        if 'added by ACP' in line: continue

        if '#CHAIN' in line:
            chain['line'].append(line.replace(';',''))
            chain['index'].append(i)
            chain['check'].append(False if ';' in line else True)
            
        if '#' in line: 
            string_list.append(line)
            i+=1
            continue
            
        if line.replace('\n', '').replace(' ', '').replace('\t', '') == '':
            string_list.append(line)
            i+=1
            continue
        
        if '\t' in line:
            targets['obj_name'].append(line.replace(';','').split('\t')[0])
            targets['index'].append(i)
            targets['oneline'].append(line.replace(';',''))
            targets['check'].append(0 if ';' in line else 1)

        else:
            targets['obj_name'].append(line.replace(';','').split()[0])
            targets['index'].append(i)
            targets['oneline'].append(line.replace(';',''))
            targets['check'].append(0 if ';' in line else 1)
        string_list.append(line)
        i+=1
    return targets, string_list, chain

def submit():
    for k in buttons['var'].keys():
        if buttons['var'][k].get() == 1:
            string_list[targets['index'][k]] = targets['oneline'][k]
        else:
            string_list[targets['index'][k]] = ';' + targets['oneline'][k]
    for k in range(len(chain['index'])):  
        if k == int(var_chains.get()):
            string_list[chain['index'][k]] = chain['line'][k]
        else:
            string_list[chain['index'][k]] = ';' + chain['line'][k]
            
    with open(filename, 'w') as f:
        f.write(''.join(string_list))
    root.destroy()

def check_all():
    for k in buttons['var'].keys():
        buttons['var'][k].set(1)

def uncheck_all():
    for k in buttons['var'].keys():
        buttons['var'][k].set(0)

def check_before_first():
    value = 1
    for k in buttons['var'].keys():
        this_value = buttons['var'][k].get()
        buttons['var'][k].set(value)
        if this_value == 1:
            value = 0

def check_after_first():
    value = 0
    for k in buttons['var'].keys():
        this_value = buttons['var'][k].get()
        if this_value == 1:
            value = 1
        buttons['var'][k].set(value)

def ckeck_between():
    check_indexes = []
    between_indexes = []
    for k in buttons['var'].keys():
        this_value = buttons['var'][k].get()
        if this_value == 1:
            check_indexes.append(k)
        if len(check_indexes) == 1:
            between_indexes.append(k)
        if len(check_indexes) == 2:
            between_indexes.append(k)
            break
    uncheck_all()
    for k in between_indexes:
        buttons['var'][k].set(1)

def get_targets():
    from os.path import dirname, join
    from os import startfile
    targets_file = join(dirname(filename),'targets.txt')
    string = ''
    for i in range(len(targets['obj_name'])):
        if targets['obj_name'][i][0] != '=':
            string += f"{targets['obj_name'][i]}\n"
    with open(targets_file, 'w') as f:
        f.write(string)
    startfile(f"{targets_file}")
        
def update(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
def _on_mousewheel(event):
   canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


filename = select_file()

global targets
targets, string_list, chain = get_script()

root = tk.Tk()
root.title(f'{basename(filename)}')
# root.geometry('250x250')
root.minsize(width=250, height=250)
root.attributes('-topmost',True)

# (column, row)
# (0,0) of main(root) window; check list of targets
box = tk.Canvas(root,width=300,height=600, borderwidth=1, relief="solid")
box.grid(row=0,column=0, ipadx=5, ipady=5)
canvas = tk.Canvas(box,width=290,height=600)
canvas.grid(row=1,column=0,sticky='e')
scrollbar = tk.Scrollbar(box, orient='vertical',command=canvas.yview)
scrollbar.grid(column=1, row=1,sticky = 'ns')

frame = tk.Frame(canvas)
canvas.create_window((0,0),window=frame,anchor='nw')
frame.bind("<Configure>", update)
canvas.bind_all("<MouseWheel>", _on_mousewheel)

canvas.config(yscrollcommand=scrollbar.set)

row_index=0
# label of targets
# put it in box prevent to scroll
target_label_str = f"     Targets          \t    RA"
target_label = tk.Label(box, text=target_label_str).grid(row=row_index, column=0, columnspan=3, sticky='w')
row_index +=1 

buttons = {
    'var': {},
    'checkbox': {},
}

for k in range(len(targets['index'])):
    if targets['obj_name'][k][0] == '=':
        tk.Label(frame, text=f"{targets['oneline'][k]}").grid(row=row_index, column=0, columnspan=3, sticky='w')
    elif '\t' in targets['oneline'][k]:
        buttons['var'][k] = tk.IntVar(value=targets['check'][k])
        tgt_name = targets['oneline'][k].split('\t')[0]
        tgt_ra = targets['oneline'][k].split('\t')[1]
        buttons['checkbox'][k] = tk.Checkbutton(frame, text=f'{tgt_name:12}\t{tgt_ra}', var=buttons['var'][k],onvalue=1,offvalue=0,).grid(row=row_index, column=0, columnspan=3, sticky='w')
    else:
        buttons['var'][k] = tk.IntVar(value=targets['check'][k])
        buttons['checkbox'][k] = tk.Checkbutton(frame, text=targets['obj_name'][k], var=buttons['var'][k],onvalue=1,offvalue=0,).grid(row=row_index, column=0, columnspan=3, sticky='w')
    row_index+=1


# (1,0) of main window; check list of chain
canvas_chain = tk.Canvas(root,width=200,height=600)
canvas_chain.grid(row=0,column=2,sticky = 'ns')

chain_row = 0
chain_label = tk.Label(canvas_chain, text="     Chain Script").grid(row=chain_row, column=3, sticky='w')
chain_row += 1

var_chains = tk.StringVar()

for k in range(len(chain['check'])):
    tk.Radiobutton(canvas_chain, text=chain['line'][k].replace('#CHAIN ', ''), var=var_chains, value=k).grid(row=chain_row, column=3, sticky='w')
    chain_row += 1
    if chain['check'][k]:
        var_chains.set(k)
tk.Radiobutton(canvas_chain, text='none' , var=var_chains, value=k+1).grid(row=chain_row, column=3, sticky='w')

if not any(chain['check']):
    var_chains.set(k+1)

larger_row = max([chain_row, row_index]) 

sep_label = tk.Label(root, text=' ').grid(row=larger_row, column=0, columnspan=3, sticky='w')


# (0,1) of main window;button of functions

b_width = 8
b_height = 2


# 第一排按鈕
canvas_button = tk.Canvas(root,width=200,height=600)
canvas_button.grid(row=2,column=0,sticky = 'ns')

checkbefore_button = tk.Button(canvas_button, text="check\nbefore first", width=b_width, height=b_height, command=check_before_first)
checkbefore_button.grid(row=1, column=0, sticky='w')

checkbefore_button = tk.Button(canvas_button, text="check\nafter first", width=b_width, height=b_height, command=check_after_first)
checkbefore_button.grid(row=1, column=1, sticky='w')

checkbetween_button = tk.Button(canvas_button, text="check\nbetween", width=b_width, height=b_height, command=ckeck_between)
checkbetween_button.grid(row=1, column=2, sticky='w')

submit = tk.Button(canvas_button, text="Submit", width=b_width, height=b_height, command=submit)
submit.grid(row=1, column=3, rowspan=2, sticky='w')


# 第二排按鈕
checkall_button = tk.Button(canvas_button, text="check all", width=b_width, height=b_height, command=check_all)
checkall_button.grid(row=2, column=0, sticky='w')

uncheckall_button = tk.Button(canvas_button, text="uncheck all", width=b_width, height=b_height, command=uncheck_all)
uncheckall_button.grid(row=2, column=1, sticky='w')

gettargets_button = tk.Button(canvas_button, text="get\ntargets", width=b_width, height=b_height, command=get_targets)
gettargets_button.grid(row=2, column=2, sticky='w')


root.update()
root.mainloop()