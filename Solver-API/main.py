from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

import os
import io
import base64

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return RedirectResponse(url='/main')


@app.get("/main")
async def main(request: Request, message=
               "Welcome to the quadratic equations solver."):
    return templates.TemplateResponse("index.html", 
                                      {"request": request,
                                       "message": message})

@app.get("/solve")
async def solve(a: int = Query(...),
                b: int = Query(...),
                c: int = Query(...)):
    
    D = b**2 - 4*a*c

    roots = []
    feedback = ''

    if a == 0 and b == 0 and c == 0:
        feedback = 'Any number is a solution.'
    elif a == 0 and b == 0 and c != 0:
        feedback = 'There is no solution.'
    elif a == 0 and b != 0:
        roots.append(-c/b)
    elif D > 0:
        roots.append((- b - np.sqrt(D)) / (2 * a))
        roots.append((- b + np.sqrt(D)) / (2 * a))
        roots.sort()    
    elif D == 0:
        roots.append((- b) / (2 * a))
    else:
        feedback = 'No real roots. Roots are complex numbers.'

    return JSONResponse(content={"roots": roots, 
                                 "feedback": feedback} 
                                 if feedback else {"roots": roots})

@app.post("/plot")
async def plot(request: Request, 
                    coeff_a: str = Form(...),
                    coeff_b: str = Form(...),
                    coeff_c: str = Form(...)):
    
    a = float(coeff_a)
    b = float(coeff_b)
    c = float(coeff_c)
    coefficients = [a, b, c]

    D = b**2 - 4*a*c

    roots = []
    feedback = ''

    fig = plt.figure()
    plt.xlabel('independent variable X')
    plt.ylabel('dependent variable Y')
    plt.title('Solution Plot', loc='center')

    if a == 0 and b == 0 and c == 0:
        feedback = 'Any number is a solution.'
        
        plt.axvline(0, color='black', linestyle='-')
        plt.axhline(0, color='red', linestyle='-')
        plt.text(0.5, 0.5, 'The plot is the X-axis line.'+'\n'+
                    'Any number is a solution.',
                 fontsize=14,
                 ha='center', va='bottom')

    elif a == 0 and b == 0 and c != 0:
        feedback = 'There is no solution.'
        
        plt.axvline(0, color='black', linestyle='-')
        plt.axhline(0, color='black', linestyle='-')
        plt.text(0.5, 0.5, 'No Solution. Nothing to plot.',
                 fontsize=14,
                 ha='center', va='bottom')
        
    elif a == 0 and b != 0:
        roots.append(-c/b)
        
        plt.axvline(roots[0], color='blue', linestyle='-')
        plt.axhline(0, color='black', linestyle='-')
        plt.plot(roots[0], 0, marker="o", color='red', label='root')
        plt.legend()

    elif D > 0:
        roots.append((- b - np.sqrt(D)) / (2 * a))
        roots.append((- b + np.sqrt(D)) / (2 * a))
        roots.sort()

        p = -b/(2*a)
        q = -D/(4*a)
        x = np.linspace(min(roots)-5, max(roots)+5, 100)
        y = a*x**2 + b*x + c
            
        plt.plot(p, q, marker='o', color='purple', label='min|max')
        plt.text(p, q+0.5, 
                str(round(p,2)),
                color='purple', fontsize=10,
                ha='center', va='bottom')

        plt.plot(x, y)
        plt.grid()

        plt.axvline(0, color='black', linestyle='-')
        plt.axhline(0, color='black', linestyle='-')
    
        plt.plot(roots[0], 0, marker="o", color='red', label='root')
        plt.text(roots[0], 0.5,
                    str(round(roots[0],2)), 
                    color='red', fontsize='10',
                    ha='center', va='bottom')
            
        plt.plot(roots[1], 0, marker='o', color='red')
        plt.text(roots[1], 0.5, 
                    str(round(roots[1],2)), 
                    color='red', fontsize='10',
                    ha='center', va='bottom')
        plt.legend()
    
    elif D == 0:
        roots.append((- b) / (2 * a))
    
        p = -b/(2*a)
        x = np.linspace(int(p)-5, int(p)+5, 100)
        y = a*x**2 + b*x + c
            
        plt.plot(p, 0, marker='o', color='purple', label='min|max')
        plt.text(p, 0.5, 
                str(round(p,2)),
                color='purple', fontsize=10,
                ha='center', va='bottom')

        plt.plot(x, y)
        plt.grid()

        plt.axvline(0, color='black', linestyle='-')
        plt.axhline(0, color='black', linestyle='-')

        plt.plot(roots[0], 0, marker="o", color='red', label='root')
        plt.text(roots[0], 0.5, 
                    str(round(roots[0],2)), 
                    color='red', fontsize='10',
                    ha='center', va='bottom')
        plt.legend()

    else:
        feedback = 'No real roots. Roots are complex numbers.'

        p1 = -b/(2*a)
        q1 = -D/(4*a)
        x = np.linspace(int(p1)-5, int(p1)+5, 100)
        y = a*x**2 + b*x + c

        plt.plot(p1, q1, marker='o', color='purple', label='min|max')
        plt.text(p1, q1+0.5, 
                str(round(p1,2)),
                color='purple', fontsize=10,
                ha='center', va='bottom')
        
        plt.plot(x, y)
        plt.grid()
        plt.legend()


    pngImage = io.BytesIO()
    fig.savefig(pngImage)
    pngImageB64String\
        = base64.b64encode(pngImage.getvalue()).decode('ascii')

    return templates.TemplateResponse("plot.html",
                                      {"request": request,
                                       "a": a,
                                       "b": b,
                                       "c": c,
                                       "coefficients": coefficients,
                                       "roots": roots,
                                       "feedback": feedback,
                                       "picture": pngImageB64String})

"""
# Note: 
# I require integer type for input by the URL GET-requests
# but for the HTML-input I purposefully chose float type. Everything 
# works well and I cannot see a reason for restriction to integers only.
"""

