import csv
import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracker_data.json')
ENROLL_RE = re.compile('^[A-Za-z0-9]+$')

class ValidationError(Exception):
    pass

class Store:

    def __init__(self, path):
        self.path = path
        self.students = {}
        self.subs = []
        self.load()

    def load(self):
        try:
            with open(self.path, encoding='utf-8') as fh:
                data = json.load(fh)
            self.students = data.get('students', {})
            self.subs = data.get('submissions', [])
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError):
            messagebox.showwarning('Data file', 'Could not read saved data; starting empty.')

    def save(self):
        tmp = self.path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump({'students': self.students, 'submissions': self.subs}, fh)
        os.replace(tmp, self.path)

    def add_student(self, enr, name):
        if not ENROLL_RE.match(enr):
            raise ValidationError('Enrollment must be letters/digits only.')
        if not name or not re.match("^[A-Za-z .'-]+$", name):
            raise ValidationError('Name must contain only letters and spaces.')
        if enr in self.students:
            raise ValidationError('Student already exists.')
        self.students[enr] = name
        self.save()

    @staticmethod
    def parse_marks(marks_text, max_text):
        try:
            mx = float(max_text)
            if mx <= 0:
                raise ValueError
        except ValueError:
            raise ValidationError('Max marks must be a positive number.') from None
        try:
            mk = float(marks_text)
        except ValueError:
            raise ValidationError('Marks must be a number.') from None
        if not 0 <= mk <= mx:
            raise ValidationError(f'Marks must be between 0 and {mx:g}.')
        return (mk, mx)

    def add_submission(self, enr, assignment, status, marks_text, max_text, remarks):
        if enr not in self.students:
            raise ValidationError('Select an existing student.')
        if not assignment:
            raise ValidationError('Assignment name is required.')
        if any((s['enrollment'] == enr and s['assignment'].lower() == assignment.lower() for s in self.subs)):
            raise ValidationError('This student already has that assignment.')
        marks, mx = (None, 0)
        if status == 'Completed':
            marks, mx = self.parse_marks(marks_text, max_text)
        self.subs.append({'enrollment': enr, 'assignment': assignment, 'status': status, 'marks': marks, 'max_marks': mx, 'remarks': remarks})
        self.save()

    def update_marks(self, index, marks_text, max_text):
        marks, mx = self.parse_marks(marks_text, max_text)
        sub = self.subs[index]
        sub.update(marks=marks, max_marks=mx, status='Completed')
        self.save()

    def rows(self, status, query):
        q = query.lower()
        for i, s in enumerate(self.subs):
            if status != 'All' and s['status'] != status:
                continue
            name = self.students.get(s['enrollment'], '')
            if q and q not in (s['enrollment'] + name + s['assignment']).lower():
                continue
            yield (i, s, name)

def fmt_marks(v):
    return '' if v is None else f'{v:g}'

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Assignment Tracker')
        self.geometry('980x600')
        self.store = Store(DATA_FILE)
        self._build()
        self.refresh()

    def _build(self):
        pad = {'padx': 4, 'pady': 3}
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=6)
        sf = ttk.LabelFrame(top, text='Add student')
        sf.grid(row=0, column=0, sticky='nsew', padx=4)
        self.enr_var, self.name_var = (tk.StringVar(), tk.StringVar())
        ttk.Label(sf, text='Enrollment').grid(row=0, column=0, sticky='w', **pad)
        ttk.Entry(sf, textvariable=self.enr_var, width=18).grid(row=0, column=1, **pad)
        ttk.Label(sf, text='Name').grid(row=1, column=0, sticky='w', **pad)
        ttk.Entry(sf, textvariable=self.name_var, width=18).grid(row=1, column=1, **pad)
        ttk.Button(sf, text='Add Student', command=self.add_student).grid(row=2, column=0, columnspan=2, **pad)
        sub = ttk.LabelFrame(top, text='Submission')
        sub.grid(row=0, column=1, sticky='nsew', padx=4)
        self.stu_var, self.asg_var = (tk.StringVar(), tk.StringVar())
        self.status_var = tk.StringVar(value='Pending')
        self.marks_var, self.max_var = (tk.StringVar(), tk.StringVar(value='20'))
        self.rem_var, self.late_var = (tk.StringVar(), tk.BooleanVar())
        ttk.Label(sub, text='Student').grid(row=0, column=0, sticky='w', **pad)
        self.stu_box = ttk.Combobox(sub, textvariable=self.stu_var, width=24, state='readonly')
        self.stu_box.grid(row=0, column=1, columnspan=3, **pad)
        ttk.Label(sub, text='Assignment').grid(row=1, column=0, sticky='w', **pad)
        ttk.Entry(sub, textvariable=self.asg_var, width=24).grid(row=1, column=1, columnspan=3, **pad)
        ttk.Label(sub, text='Status').grid(row=2, column=0, sticky='w', **pad)
        ttk.Radiobutton(sub, text='Pending', variable=self.status_var, value='Pending').grid(row=2, column=1, **pad)
        ttk.Radiobutton(sub, text='Completed', variable=self.status_var, value='Completed').grid(row=2, column=2, **pad)
        ttk.Label(sub, text='Marks / Max').grid(row=3, column=0, sticky='w', **pad)
        ttk.Entry(sub, textvariable=self.marks_var, width=8).grid(row=3, column=1, **pad)
        ttk.Entry(sub, textvariable=self.max_var, width=8).grid(row=3, column=2, **pad)
        ttk.Label(sub, text='Remarks').grid(row=4, column=0, sticky='w', **pad)
        ttk.Entry(sub, textvariable=self.rem_var, width=24).grid(row=4, column=1, columnspan=2, **pad)
        ttk.Checkbutton(sub, text='Late', variable=self.late_var).grid(row=4, column=3, **pad)
        ttk.Button(sub, text='Add Submission', command=self.add_submission).grid(row=5, column=1, **pad)
        ttk.Button(sub, text='Update Marks (selected)', command=self.update_marks).grid(row=5, column=2, columnspan=2, **pad)
        bar = ttk.Frame(self)
        bar.pack(fill='x', padx=8)
        self.filter_var, self.search_var = (tk.StringVar(value='All'), tk.StringVar())
        for label in ('All', 'Pending', 'Completed'):
            ttk.Radiobutton(bar, text=label, variable=self.filter_var, value=label, command=self.refresh).pack(side='left', padx=4)
        ttk.Label(bar, text='Search:').pack(side='left', padx=(16, 2))
        ttk.Entry(bar, textvariable=self.search_var, width=24).pack(side='left')
        self.search_var.trace_add('write', lambda *_: self.refresh())
        ttk.Button(bar, text='Export CSV', command=self.export_csv).pack(side='right')
        self.count_lbl = ttk.Label(bar, text='')
        self.count_lbl.pack(side='right', padx=10)
        cols = ('enrollment', 'name', 'assignment', 'status', 'marks', 'max', 'remarks')
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=8, pady=6)
        self.tree = ttk.Treeview(frame, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=90 if c in ('marks', 'max') else 130)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for i, s, name in self.store.rows(self.filter_var.get(), self.search_var.get()):
            self.tree.insert('', 'end', iid=str(i), values=(s['enrollment'], name, s['assignment'], s['status'], fmt_marks(s['marks']), fmt_marks(s['max_marks']) if s['marks'] is not None else '', s['remarks']))
            shown += 1
        self.count_lbl.config(text=f'{shown} of {len(self.store.subs)} records')
        self.stu_box['values'] = [f'{e} - {n}' for e, n in sorted(self.store.students.items())]

    def add_student(self):
        try:
            self.store.add_student(self.enr_var.get().strip(), self.name_var.get().strip())
        except ValidationError as exc:
            messagebox.showerror('Invalid input', str(exc))
            return
        self.enr_var.set('')
        self.name_var.set('')
        self.refresh()

    def add_submission(self):
        enr = self.stu_var.get().split(' - ')[0].strip()
        remarks = self.rem_var.get().strip()
        if self.late_var.get():
            remarks = ('Late. ' + remarks).strip()
        try:
            self.store.add_submission(enr, self.asg_var.get().strip(), self.status_var.get(), self.marks_var.get().strip(), self.max_var.get().strip(), remarks)
        except ValidationError as exc:
            messagebox.showerror('Invalid input', str(exc))
            return
        self.asg_var.set('')
        self.marks_var.set('')
        self.rem_var.set('')
        self.late_var.set(False)
        self.refresh()

    def update_marks(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('Update marks', 'Select a row first.')
            return
        try:
            self.store.update_marks(int(sel[0]), self.marks_var.get().strip(), self.max_var.get().strip())
        except ValidationError as exc:
            messagebox.showerror('Invalid input', str(exc))
            return
        self.refresh()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', initialfile='report.csv', filetypes=[('CSV', '*.csv')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh)
                w.writerow(['enrollment', 'name', 'assignment', 'status', 'marks', 'remarks'])
                for _, s, name in self.store.rows('All', ''):
                    w.writerow([s['enrollment'], name, s['assignment'], s['status'], fmt_marks(s['marks']), s['remarks']])
        except OSError as exc:
            messagebox.showerror('Export failed', str(exc))
            return
        messagebox.showinfo('Export', f'Report saved to {path}')
if __name__ == '__main__':
    App().mainloop()
