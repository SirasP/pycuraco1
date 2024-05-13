from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors, hashlib, re


app= Flask(__name__, template_folder='sitio')

app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin1"
app.config["MYSQL_DB"] = "flutter"

mysql = MySQL(app)
app.secret_key = 'SecrEtKEy'

@app.route('/', methods=['GET','POST'])
def inicio():
   
    if request.method == 'POST' and 'user' in request.form and 'pass' in request.form:
      
        username = request.form['user']
        password = request.form['pass']
      
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM loginusuario WHERE usuario = %s AND pass = %s', (username, password,))
        account = cursor.fetchone()
        
        if account:
            
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['usuario']
                   
            return redirect("/table")
        else:
           
            flash('Usuario Y/O Contraseña Incorrecta',"danger")
            return render_template('/index.html')
        
    return render_template("index.html")

@app.route('/table', methods=['POST','GET'])
def tabla():
    if 'loggedin' in session:
       
        sql = "select * from loginusuario"
        cur = mysql.connection.cursor()
        cur.execute(sql)
        rv = cur.fetchall()
        
        return render_template('/table.html', rvs=rv, username=session['username'])
    
    return redirect(url_for('inicio'))
 
@app.route("/registrar", methods=['POST','GET'])
def registrarUsuario():
    
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            
            username = request.form['username']
            password = request.form['password']
            repassword = request.form["repassword"] 
            email = request.form['email'] 
            nombre = request.form["nombre"] 
            apellido = request.form["apellido"]
            
           
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM loginusuario WHERE usuario = %s', (username,))
            account = cursor.fetchone()
           
            if account:
                
                flash('Nombre de Usuario Existente!',"primary")
            elif not username or not password or not email:
                
                flash('RUN SOLO DEBE CONTENER NUMEROS',"danger")
            else:
                
                hash = password + app.secret_key
                hash = hashlib.sha1(hash.encode())
                password = hash.hexdigest()
                
                hash = repassword + app.secret_key
                hash = hashlib.sha1(hash.encode())
                repassword = hash.hexdigest()
                                
                cursor.execute('INSERT INTO loginusuario VALUES (NULL, %s, %s, %s, %s, %s, %s)', 
                               (username, nombre, apellido, password, repassword, email,))
                mysql.connection.commit()
                               
                flash('Registro Exitoso!',"primary")
            
    elif request.method == 'POST':
        flash('Por favor, Rellenar Los campos')
    return render_template("registrar.html")

@app.route('/borrar/<string:id>')
def borrar(id):
    if 'loggedin' in session:
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('delete from loginusuario where id = %s', (id,))
        mysql.connection.commit()
        
        flash("Eliminado el registro","primary")
        return redirect(url_for('tabla'))
    
    return render_template('/index.html')

@app.route("/usuariosCuraco")
def usuariosCuraco():
    if "loggedin" in session:
        
        sql = "select * from usuariocuraco"
        cur = mysql.connection.cursor()
        cur.execute(sql)
        rv = cur.fetchall()
    
    return render_template("usuariosCuraco.html", rvs = rv, username = session['username'])

@app.route("/agregarUsuario", methods=['POST','GET'])
def agregarUsuarioCuraco():
   
    if request.method == 'POST':
            
            rut = request.form["rut"]
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            direccion = request.form["direccion"] 
            fechacreacion = request.form['fechacreacion'] 
           
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM usuariocuraco WHERE rut = %s', (rut,))
            account = cursor.fetchone()
           
            if account:
                flash('Rut Existente',"danger")
                
            elif not rut :
                flash('Por favor, Rellenar Los campos',"danger")
            else:
                
                cursor.execute('INSERT INTO usuariocuraco VALUES (NULL, %s, %s, %s, %s, %s, %s)', 
                               (nombre, apellido, direccion, fechacreacion, 'NULL', rut,))
                mysql.connection.commit()
                               
                flash('Registro Exitoso!',"primary")
                
    elif request.method == 'POST':
        flash('Por favor, Rellenar Los campos')
        return redirect(url_for("usuariosCuraco"))
    return render_template("agregarUsuario.html")

@app.route("/borrarCuraco/<string:id>")
def borrarCuraco(id):
    if 'loggedin' in session:
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('delete from usuariocuraco where id = %s', (id,))
        mysql.connection.commit()
        
        flash("Eliminado el registro")
        return redirect(url_for('usuariosCuraco'))
    
    return render_template('/borrarCuraco.html')

@app.route("/IngresoCuraco", methods = ['GET','POST'])
def IngresoCuraco():
    if "loggedin" in session:
        if request.method == 'POST' and 'rut' in request.form:
            
            rut = request.form['rut']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM usuariocuraco WHERE rut = %s', (rut,))
            rv = cursor.fetchall()
            
            flash("Busqueda exitosa!","primary")
            return render_template('/IngresoCuraco.html', rvs=rv, username=session["username"],rut = rut)
    
    return render_template("/IngresoCuraco.html")


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   
   flash("Termino de Sesion","error")
   
   return redirect(url_for('inicio'))
 
@app.route("/IngresoCuraco", methods = ['POST'])
def ingresopatente():
    
    if request.method == 'POST' and 'rut' in request.form :
                  
        rut = request.form["rut"]
        nombre = request.form["nombre"]
        patente = request.form["patente"]
        Capacidadcarga = request.form["Capacidadcarga"]
        marca = request.form["marca"]
        modelo = request.form["modelo"]
        valor = request.form["valor"]
        
        print(rut)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO ingresocuraco VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)',(rut, nombre, patente, Capacidadcarga, marca, modelo,valor,))
       
        mysql.connection.commit()
  
        
        return render_template("/index.html")
    print(rut) 
    flash("ok","danger")
    return render_template("/index.html")   
 
  
if __name__ == '__main__':
    app.run(debug=True)